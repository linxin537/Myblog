from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
from app.config import get_settings

settings = get_settings()

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int, remember_me: bool = False) -> str:
    days = 30 if remember_me else settings.REFRESH_TOKEN_EXPIRE_DAYS
    expire = datetime.utcnow() + timedelta(days=days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def is_locked(user) -> bool:
    if user.locked_until and user.locked_until > datetime.utcnow():
        return True
    if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
        return True
    return False


def record_login_failure(user) -> tuple[int, datetime | None]:
    attempts = user.login_attempts + 1
    locked_until = None
    if attempts >= MAX_LOGIN_ATTEMPTS:
        locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
    return attempts, locked_until


def reset_login_attempts(user):
    user.login_attempts = 0
    user.locked_until = None
