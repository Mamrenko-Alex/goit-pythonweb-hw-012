import pytest
from fastapi import status
from jose import jwt
import os
# from schemas import PasswordResetRequest, PasswordResetConfirm

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = "HS256"


def create_token(sub: str):
    return jwt.encode({"sub": sub}, SECRET_KEY, algorithm=ALGORITHM)


def test_forgot_password_success(client, test_db, fake_user):
    response = client.post("/auth/forgot-password",
                           json={"email": fake_user.email})
    print(response.status_code)
    print(response.headers.get("content-type"))
    print(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert "Інструкція" in response.json()["message"]


def test_forgot_password_user_not_found(client):
    response = client.post("/auth/forgot-password",
                           json={"email": "unknown@example.com"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Користувача не знайдено"


def test_reset_password_success(client, test_db, fake_user):
    token = create_token(fake_user.email)
    new_password = "new_secure_pass"

    response = client.post("/auth/reset-password", json={
        "token": token,
        "new_password": new_password
    })

    assert response.status_code == status.HTTP_200_OK
    assert "успішно" in response.json()["message"]

    # Перевіримо, що можна залогінитись з новим паролем
    login_resp = client.post("/auth/login", json={
        "email": fake_user.email,
        "password": new_password
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


def test_reset_password_invalid_token(client):
    response = client.post("/auth/reset-password", json={
        "token": "bad.token.here",
        "new_password": "whatever"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Невалідний" in response.json()["detail"]


def test_reset_password_user_not_found(client):
    token = create_token("ghost@example.com")
    response = client.post("/auth/reset-password", json={
        "token": token,
        "new_password": "12345"
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "не знайдено" in response.json()["detail"]
