from datetime import datetime
from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.schemas.common import ApiResponse, success_response, error_response
from app.schemas.password import ChangePasswordRequest
from app.services import log_action
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, is_locked, record_login_failure, reset_login_attempts,
)
from app.core.errors import (
    UsernameExistsError, EmailExistsError, LoginError, AccountLockedError,
    UnauthorizedError, ValidationError,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


def _set_token_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie("access_token", access_token, httponly=True, samesite="lax", max_age=7200)
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="lax", max_age=604800)


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise UsernameExistsError()

    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise EmailExistsError()

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        role=UserRole.reader,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return success_response(data=UserResponse.model_validate(user))


@router.post("/login")
async def login(req: LoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        if user:
            user.login_attempts, user.locked_until = record_login_failure(user)
            await db.commit()
        raise LoginError()

    if is_locked(user):
        raise AccountLockedError()

    if not user.is_active:
        raise LoginError()

    reset_login_attempts(user)
    await log_action(db, action="login", user_id=user.id, target_type="user", target_id=user.id, request=request)

    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id, remember_me=req.remember_me)

    _set_token_cookies(response, access_token, refresh_token)

    return success_response(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(),
    })


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise UnauthorizedError("缺少 Refresh Token")

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedError("无效的 Refresh Token")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedError("用户不存在或已禁用")

    new_access = create_access_token(user.id, user.role.value)
    new_refresh = create_refresh_token(user.id)

    _set_token_cookies(response, new_access, new_refresh)

    return success_response(data={
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    })


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return success_response(message="已登出")


@router.put("/password")
async def change_password(
    req: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(req.old_password, current_user.hashed_password):
        return error_response(2003, "旧密码不正确")

    if len(req.new_password) < 8:
        return error_response(1001, "新密码长度至少 8 位")

    current_user.hashed_password = hash_password(req.new_password)
    await db.flush()

    await log_action(db, action="change_password", user_id=current_user.id,
                     target_type="user", target_id=current_user.id, request=request)

    return success_response(message="密码修改成功")
