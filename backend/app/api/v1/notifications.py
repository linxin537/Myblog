from fastapi import APIRouter, Depends
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user

router = APIRouter(tags=["notifications"])


@router.get("/notifications")
async def list_notifications(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id
        )
    )
    total = total.scalar() or 0

    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    notifications = result.scalars().all()

    return success_response(
        data={
            "items": [
                NotificationResponse.model_validate(n) for n in notifications
            ],
            "total": total,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }
    )


@router.put("/notifications/{notification_id}/read")
async def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        return error_response(1004, "通知不存在")

    notification.is_read = True
    await db.flush()
    return success_response(data=NotificationResponse.model_validate(notification))


@router.put("/notifications/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.flush()
    return success_response()


@router.get("/notifications/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    count = result.scalar() or 0
    return success_response(data={"count": count})
