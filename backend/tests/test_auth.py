import pytest
import httpx


async def test_register_success(client: httpx.AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Pass1234",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["username"] == "testuser"
    assert data["data"]["role"] == "reader"


async def test_register_duplicate_username(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "dupuser", "email": "first@example.com", "password": "Pass1234",
    })
    resp = await client.post("/api/v1/auth/register", json={
        "username": "dupuser", "email": "second@example.com", "password": "Pass1234",
    })
    assert resp.status_code == 409
    data = resp.json()
    assert data["code"] == 2001


async def test_register_duplicate_email(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "user_a", "email": "same@example.com", "password": "Pass1234",
    })
    resp = await client.post("/api/v1/auth/register", json={
        "username": "user_b", "email": "same@example.com", "password": "Pass1234",
    })
    assert resp.status_code == 409
    data = resp.json()
    assert data["code"] == 2002


async def test_login_success(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser", "email": "login@example.com", "password": "Pass1234",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "username": "loginuser", "password": "Pass1234",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["access_token"]
    assert data["data"]["user"]["username"] == "loginuser"
    assert "access_token" in resp.cookies


async def test_login_wrong_password(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "wrongpw", "email": "wrong@example.com", "password": "Pass1234",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "username": "wrongpw", "password": "BadPass1",
    })
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == 2003


async def test_login_locked_account(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "lockme", "email": "lock@example.com", "password": "Pass1234",
    })
    for _ in range(5):
        await client.post("/api/v1/auth/login", json={
            "username": "lockme", "password": "WrongPass1",
        })
    resp = await client.post("/api/v1/auth/login", json={
        "username": "lockme", "password": "Pass1234",
    })
    assert resp.status_code == 423
    data = resp.json()
    assert data["code"] == 2004
