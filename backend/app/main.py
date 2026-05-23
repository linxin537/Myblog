from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import engine, Base
from app.models import User  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.password_reset import PasswordResetToken  # noqa: F401
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.categories import router as categories_router
from app.api.v1.tags import router as tags_router
from app.api.v1.articles import router as articles_router
from app.api.v1.files import router as files_router
from app.api.v1.comments import router as comments_router
from app.api.v1.admin import router as admin_router
from app.api.v1.rss import router as rss_router
from app.api.v1.sitemap import router as sitemap_router
from app.api.v1.notifications import router as notifications_router
from app.core.errors import AppError
from app.core.middleware import RateLimitMiddleware
from app.schemas.common import error_response
import os

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    await engine.dispose()


app = FastAPI(
    title="个人博客平台 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.environ.get("TESTING"):
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(articles_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(rss_router, prefix="/api/v1")
app.include_router(sitemap_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.error_code, exc.detail["message"] if isinstance(exc.detail, dict) else str(exc.detail)),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"code": 9999, "message": str(exc), "data": None},
    )


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "database": "connected"}
