from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from redis_client import redis_client
from models import User
from schemas import UserResponse
from database import get_db
import os
import json

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    # 1. Спробуємо з Redis
    cached_user = redis_client.get(f"user:{user_id}")
    if cached_user is not None:
        try:
            user_data = json.loads(cached_user)
            return UserResponse(**user_data)
        except (json.JSONDecodeError, TypeError):
            pass  # Йдемо до БД

    # 2. Якщо немає — йдемо до БД
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # 3. Кешуємо знову
    user_data = UserResponse.model_validate(user).model_dump()
    redis_client.set(f"user:{user.id}", json.dumps(user_data), ex=3600)

    return UserResponse(**user_data)
