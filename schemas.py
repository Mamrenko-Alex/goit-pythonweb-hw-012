from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class ContactBase(BaseModel):
    """Базова модель для контактів."""
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date


class ContactCreate(ContactBase):
    """Модель для створення нового контакту."""
    pass


class ContactUpdate(ContactBase):
    """Модель для оновлення існуючого контакту."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[date] = None


class ContactResponse(ContactBase):
    """Модель для відповіді з інформацією про контакт."""
    id: int

    class Config:
        """Конфігурація для Pydantic моделей."""
        from_attributes = True


class UserCreate(BaseModel):
    """Модель для створення нового користувача."""
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Модель для відповіді з інформацією про користувача."""
    id: int
    username: str
    email: EmailStr
    is_verified: bool
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Модель для токена доступу."""
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    """Модель для логіну користувача."""
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
