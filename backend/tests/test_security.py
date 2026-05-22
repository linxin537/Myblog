from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    is_locked,
    record_login_failure,
    reset_login_attempts,
    MAX_LOGIN_ATTEMPTS,
)


@dataclass
class StubUser:
    login_attempts: int = 0
    locked_until: datetime | None = None


def test_verify_password_correct():
    hashed = hash_password("my-secret-123")
    assert verify_password("my-secret-123", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("my-secret-123")
    assert verify_password("wrong-password", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token(user_id=1, role="admin")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_refresh_token_roundtrip():
    token = create_refresh_token(user_id=42, remember_me=False)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"


def test_decode_invalid_token_returns_none():
    assert decode_token("not.a.valid.token") is None
    assert decode_token("") is None


def test_is_locked_under_threshold():
    user = StubUser(login_attempts=3)
    assert is_locked(user) is False


def test_is_locked_at_threshold():
    user = StubUser(login_attempts=MAX_LOGIN_ATTEMPTS)
    assert is_locked(user) is True


def test_is_locked_when_locked_until_in_future():
    future = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
    user = StubUser(login_attempts=2, locked_until=future)
    assert is_locked(user) is True


def test_is_locked_when_locked_until_passed():
    past = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    user = StubUser(login_attempts=2, locked_until=past)
    assert is_locked(user) is False


def test_record_login_failure_increments():
    user = StubUser(login_attempts=2)
    attempts, locked_until = record_login_failure(user)
    assert attempts == 3
    assert locked_until is None


def test_record_login_failure_locks_at_max():
    user = StubUser(login_attempts=MAX_LOGIN_ATTEMPTS - 1)
    attempts, locked_until = record_login_failure(user)
    assert attempts == MAX_LOGIN_ATTEMPTS
    assert locked_until is not None


def test_is_locked_expired_lockout_with_max_attempts():
    """锁定期已过但失败次数仍为最大值时，不应再锁定"""
    past = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=20)
    user = StubUser(login_attempts=MAX_LOGIN_ATTEMPTS, locked_until=past)
    assert is_locked(user) is False


def test_reset_login_attempts():
    user = StubUser(login_attempts=4, locked_until=datetime.now(timezone.utc).replace(tzinfo=None))
    reset_login_attempts(user)
    assert user.login_attempts == 0
    assert user.locked_until is None
