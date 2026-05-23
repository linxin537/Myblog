import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File as FileParam, Form
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.file import File
from app.schemas.file import FileResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user

router = APIRouter(prefix="/files", tags=["文件"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = FileParam(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        return error_response(1001, f"不支持的文件类型: {file.content_type}")

    content = await file.read()
    from app.config import get_settings
    settings = get_settings()

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        return error_response(1001, f"文件大小超过 {settings.MAX_FILE_SIZE_MB}MB 限制")

    ext = os.path.splitext(file.filename or "image.png")[1].lower() or ".png"
    name = uuid.uuid4().hex
    date_dir = datetime.utcnow().strftime("%Y/%m")
    # Resolve upload dir relative to backend root (not CWD)
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_base = os.path.join(backend_root, "static", "uploads")
    rel_dir = os.path.join(upload_base, date_dir)
    os.makedirs(rel_dir, exist_ok=True)

    file_path = os.path.join(rel_dir, f"{name}{ext}")
    with open(file_path, "wb") as f:
        f.write(content)

    thumb_path = None
    if file.content_type != "image/svg+xml":
        thumb_path = _generate_thumbnail(file_path, rel_dir, name, ext)

    file_record = File(
        original_name=file.filename or "untitled",
        path=file_path,
        size=len(content),
        mime_type=file.content_type,
        uploader_id=current_user.id,
    )
    db.add(file_record)
    await db.flush()
    await db.refresh(file_record)

    stmt = select(File).options(selectinload(File.uploader)).where(File.id == file_record.id)
    file_record = (await db.execute(stmt)).scalar_one()

    data = FileResponse.model_validate(file_record).model_dump()
    if thumb_path:
        data["thumb_path"] = thumb_path

    return success_response(data=data)


def _generate_thumbnail(file_path: str, rel_dir: str, name: str, ext: str) -> str | None:
    try:
        from PIL import Image
        img = Image.open(file_path)
        img.thumbnail((400, 400))
        thumb_name = f"{name}_thumb{ext}"
        thumb_full = os.path.join(rel_dir, thumb_name)
        img.save(thumb_full, quality=85)
        return thumb_full
    except Exception:
        return None


@router.get("")
async def get_files(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(File)
        .options(selectinload(File.uploader))
        .where(File.uploader_id == current_user.id, File.deleted_at.is_(None))
        .order_by(File.id.desc())
    )

    count_stmt = select(func.count()).select_from(File).where(
        File.uploader_id == current_user.id, File.deleted_at.is_(None)
    )
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    files = result.scalars().all()

    return {
        "code": 0,
        "message": "ok",
        "data": [FileResponse.model_validate(f).model_dump() for f in files],
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }
