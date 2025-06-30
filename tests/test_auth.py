import pytest
from fastapi import HTTPException
from jose import jwt
from dependencies import get_current_user  # або де у тебе ця функція
from models import User
from sqlalchemy.orm import Session
import os

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = "HS256"


def create_token(sub):
    return jwt.encode({"sub": str(sub)}, SECRET_KEY, algorithm=ALGORITHM)


def test_get_current_user_valid_token(test_db: Session, fake_user):
    token = create_token(fake_user.id)
    user = get_current_user(token=token, db=test_db)
    assert user.id == fake_user.id
    assert user.email == fake_user.email


def test_get_current_user_invalid_token_signature(test_db: Session):
    # Підпис інший
    bad_token = jwt.encode({"sub": "1"}, "wrong-secret", algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=bad_token, db=test_db)
    assert exc_info.value.status_code == 401
    assert "credentials" in exc_info.value.detail


def test_get_current_user_missing_sub_claim(test_db: Session):
    token = jwt.encode({"no_sub": "123"}, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=test_db)
    assert exc_info.value.status_code == 401


def test_get_current_user_user_not_found(test_db: Session):
    # Створюємо токен з неіснуючим ID
    token = create_token(999999)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=test_db)
    assert exc_info.value.status_code == 401
