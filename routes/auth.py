from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserResponse, Token, UserLogin, PasswordResetRequest, PasswordResetConfirm
from database import get_db
from passlib.context import CryptContext
from jwt_utils import create_access_token, decode_access_token
from services.email_service import send_email_for_verification, send_password_reset_email
import crud
from redis_client import redis_client
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Хешує пароль користувача для зберігання в базі даних."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє, чи збігається введений пароль з хешованим паролем."""
    return pwd_context.verify(plain_password, hashed_password)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Реєстрація нового користувача."""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Користувач вже існує")

    hashed_password = get_password_hash(user.password)
    user = User(email=user.email, password=hashed_password,
                username=user.username)
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email})
    verify_link = f"http://localhost:8000/auth/verify?token={token}"

    send_email_for_verification(user.email, verify_link)
    return user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Логін користувача та отримання токена доступу."""
    user = crud.get_user_by_email(db, user_data.email)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Невірна пошта або пароль")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email не підтверджено")

    token = create_access_token(data={"sub": user.id})

    from schemas import UserResponse
    user_data = UserResponse.model_validate(user).model_dump()
    redis_client.setex(f"user:{user.id}", 3600,
                       json.dumps(user_data))  # TTL = 1 год

    return {"access_token": token, "token_type": "bearer"}


@router.get("/verify", status_code=200)
def verify_email(token: str, db: Session = Depends(get_db)):
    """Підтвердження email користувача за токеном."""
    email = decode_access_token(token)
    if email is None:
        raise HTTPException(status_code=400, detail="Невалідний токен")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if user.is_verified:
        return {"message": "Email вже підтверджено ✅"}

    user.is_verified = True
    db.commit()
    return {"message": "Email підтверджено успішно ✅"}


@router.post("/forgot-password")
def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    token = create_access_token(
        {"sub": user.email}, expires_delta=3600)  # на 1 годину
    reset_link = f"http://localhost:8000/auth/reset-password?token={token}"
    send_password_reset_email(user.email, reset_link)

    return {"message": "Інструкція для скидання пароля надіслана на email"}


@router.post("/reset-password")
def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    email = decode_access_token(data.token)
    if not email:
        raise HTTPException(
            status_code=400, detail="Невалідний або прострочений токен")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    user.password = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Пароль змінено успішно ✅"}
