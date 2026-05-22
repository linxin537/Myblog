from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.core.security import decode_token
from app.core.errors import UnauthorizedError, ForbiddenError


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise UnauthorizedError()

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("无效的 Token")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedError("用户不存在或已禁用")

    return user


def require_role(*roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("角色权限不足")
        return current_user
    return role_checker
