import pytest
from jwt_utils import create_access_token, decode_access_token
from datetime import timedelta
import time
import jose.jwt as jwt

SECRET_KEY = "super-secret"
ALGORITHM = "HS256"


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "test@example.com"})
    assert isinstance(token, str)


def test_token_contains_correct_subject():
    email = "user@example.com"
    token = create_access_token({"sub": email})
    decoded = decode_access_token(token)
    assert decoded == email


def test_token_expires_properly():
    token = create_access_token(
        {"sub": "expired@example.com"}, expires_delta=timedelta(seconds=1))
    time.sleep(2)
    decoded = decode_access_token(token)
    assert decoded is None


def test_invalid_token_returns_none():
    invalid_token = "not.a.valid.token"
    decoded = decode_access_token(invalid_token)
    assert decoded is None


def test_token_with_wrong_key_fails():
    wrong_key = "WRONG_SECRET"
    token = jwt.encode({"sub": "test@example.com"},
                       wrong_key, algorithm="HS256")

    email = decode_access_token(token)
    assert email is None
