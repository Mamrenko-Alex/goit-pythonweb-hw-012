from sqlalchemy.orm import Session
from models import Contact, User
from schemas import ContactCreate, ContactUpdate, UserCreate
from datetime import date, timedelta
from datetime import datetime
from passlib.context import CryptContext
from fastapi import HTTPException, status


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_contacts_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()


def get_contact_by_id(db: Session, contact_id: int, user_id: int):
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()


def create_contact(db: Session, contact: ContactCreate, user_id: int):
    db_contact = Contact(
        **contact.dict(), created_at=datetime.utcnow(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, updated_data: ContactUpdate, user_id: int):
    contact = get_contact_by_id(db, contact_id, user_id)
    if contact:
        updated_fields = updated_data.dict(exclude_unset=True)
        for key, value in updated_fields.items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    contact = get_contact_by_id(db, contact_id, user_id)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def upcoming_birthdays(db: Session, user_id: int):
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(
        Contact.user_id == user_id,
        Contact.birthday.between(today, next_week)
    ).all()


def search_contacts(db: Session, query: str, user_id: int):
    return db.query(Contact).filter(
        Contact.user_id == user_id,
        (
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
    ).all()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already exists")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
