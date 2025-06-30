from redis_client import redis_client
from dependencies import get_current_user
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from jose import jwt
from dependencies import get_current_user  # або де у тебе ця функція
from models import User
from sqlalchemy.orm import Session
import os
from schemas import UserResponse
import json

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = "HS256"


def create_token(sub):
    return jwt.encode({"sub": str(sub)}, SECRET_KEY, algorithm=ALGORITHM)


def test_get_current_user_uses_cache(fake_user):
    token = create_token(fake_user.id)

    # cached = UserResponse.model_validate(fake_user).model_dump()
    cached = {
        "id": fake_user.id,
        "username": fake_user.username,
        "email": fake_user.email,
        "is_verified": fake_user.is_verified,
        "avatar_url": fake_user.avatar_url or None,
    }

    redis_client.set(f"user:{fake_user.id}", json.dumps(cached))

    mock_db = MagicMock()  # БД не повинна використовуватись

    user = get_current_user(token=token, db=mock_db)
    assert user.email == fake_user.email
    assert isinstance(user, UserResponse)
    mock_db.query.assert_not_called()


def test_get_current_user_valid_token(test_db: Session, fake_user):
    token = create_token(fake_user.id)
    from redis_client import redis_client
    from schemas import UserResponse
    import json

    # додамо вручну кеш
    user_data = UserResponse.model_validate(fake_user).model_dump()
    redis_client.set(f"user:{fake_user.id}", json.dumps(user_data))

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
