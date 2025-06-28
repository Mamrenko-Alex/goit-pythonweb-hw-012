from sqlalchemy import ForeignKey, Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Contact(Base):
    """Модель для зберігання контактів користувача."""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    birthday = Column(Date)
    created_at = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="contacts")


class User(Base):
    """Модель для зберігання користувачів."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # зберігаємо хеш
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
