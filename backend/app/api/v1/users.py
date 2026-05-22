from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse, UpdateUserRequest
from app.schemas.common import success_response
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    return success_response(data=UserResponse.model_validate(current_user).model_dump())


@router.put("/me", response_model=dict)
async def update_me(
    req: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.avatar is not None:
        current_user.avatar = req.avatar
    if req.bio is not None:
        current_user.bio = req.bio
    await db.flush()
    await db.refresh(current_user)
    return success_response(data=UserResponse.model_validate(current_user).model_dump())
