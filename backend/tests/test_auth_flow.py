from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.core.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_login_refresh_and_logout():
    register_response = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "StrongPass#2026"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "StrongPass#2026"},
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["token_type"] == "bearer"
    assert "access_token" in login_payload
    assert "refresh_token" in login_payload

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": login_payload["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()

    me_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {refresh_payload['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "alice@example.com"

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_payload["refresh_token"]},
        headers={"Authorization": f"Bearer {refresh_payload['access_token']}"},
    )
    assert logout_response.status_code == 200

    refresh_after_logout = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_payload["refresh_token"]},
    )
    assert refresh_after_logout.status_code == 401


def test_password_reset_flow():
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "StrongPass#2026"},
    )

    request_reset_response = client.post(
        "/auth/request-password-reset",
        json={"email": "bob@example.com"},
    )
    assert request_reset_response.status_code == 200

    payload = request_reset_response.json()
    assert "debug_token" in payload
    assert payload["debug_token"]

    reset_response = client.post(
        "/auth/reset-password",
        json={"token": payload["debug_token"], "new_password": "NewStrong#2027"},
    )
    assert reset_response.status_code == 200

    old_login_response = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "StrongPass#2026"},
    )
    assert old_login_response.status_code == 401

    new_login_response = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "NewStrong#2027"},
    )
    assert new_login_response.status_code == 200
