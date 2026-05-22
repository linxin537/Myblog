from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.schemas.admin import UserManageResponse, UpdateRoleRequest, UpdateStatusRequest, AuditLogResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user, require_role
from app.services import log_action

router = APIRouter(tags=["管理后台"])


# ==================== 审计日志 ====================

@router.get("/admin/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: str | None = Query(None),
    user_id: int | None = Query(None),
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AuditLog).options(joinedload(AuditLog.user))

    if action:
        stmt = stmt.where(AuditLog.action == action)
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    logs = result.unique().scalars().all()

    data = []
    for log in logs:
        d = AuditLogResponse.model_validate(log).model_dump()
        d["username"] = log.user.username if log.user else None
        data.append(d)

    return {
        "code": 0, "message": "ok",
        "data": data,
        "pagination": {"total": total, "page": page, "page_size": page_size,
                        "total_pages": (total + page_size - 1) // page_size},
    }


# ==================== 用户管理 ====================

@router.get("/admin/users")
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    search: str | None = Query(None),
    role: str | None = Query(None),
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.deleted_at.is_(None))

    if search:
        stmt = stmt.where((User.username.contains(search)) | (User.email.contains(search)))
    if role:
        try:
            UserRole(role)
            stmt = stmt.where(User.role == role)
        except ValueError:
            return error_response(1001, "无效的角色值")

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(User.id.asc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return {
        "code": 0, "message": "ok",
        "data": [UserManageResponse.model_validate(u).model_dump() for u in users],
        "pagination": {"total": total, "page": page, "page_size": page_size,
                        "total_pages": (total + page_size - 1) // page_size},
    }


@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    req: UpdateRoleRequest,
    request: Request,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        return error_response(1005, "不能修改自己的角色")

    try:
        new_role = UserRole(req.role)
    except ValueError:
        return error_response(1001, "无效的角色值，必须为 admin/author/reader")

    result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if not user:
        return error_response(1004, "用户不存在")

    old_role = user.role.value
    user.role = new_role
    await db.flush()

    await log_action(db, action="update_role", user_id=current_user.id,
                     target_type="user", target_id=user_id, request=request,
                     detail=f"{old_role} -> {req.role}")

    return success_response(data=UserManageResponse.model_validate(user).model_dump())


@router.put("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    req: UpdateStatusRequest,
    request: Request,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        return error_response(1005, "不能禁用自己")

    result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if not user:
        return error_response(1004, "用户不存在")

    user.is_active = req.is_active
    await db.flush()

    await log_action(db, action="toggle_user_status", user_id=current_user.id,
                     target_type="user", target_id=user_id, request=request,
                     detail=f"active={req.is_active}")

    return success_response(data=UserManageResponse.model_validate(user).model_dump())
