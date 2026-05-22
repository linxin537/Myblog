from pydantic import BaseModel
from datetime import datetime
from app.schemas.auth import UserResponse

class FileResponse(BaseModel):
    id: int
    original_name: str
    path: str
    size: int
    mime_type: str
    uploader_id: int
    created_at: datetime
    
    uploader: UserResponse | None = None

    model_config = {"from_attributes": True}
