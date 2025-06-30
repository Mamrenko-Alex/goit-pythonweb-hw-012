import pytest
from crud import (create_contact, get_contact_by_id, get_contacts_for_user,
                  update_contact, delete_contact, search_contacts,
                  upcoming_birthdays, create_user, get_user_by_email)
from sqlalchemy.orm import Session
from schemas import ContactCreate, ContactUpdate, UserCreate
from datetime import date, timedelta


def test_create_and_get_contact(test_db, fake_user):
    contact_in = ContactCreate(
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        phone_number="123456789",
        birthday="1990-01-01"
    )
    contact = create_contact(test_db, contact_in, fake_user.id)
    fetched = get_contact_by_id(test_db, contact.id, fake_user.id)
    assert fetched is not None
    assert contact.id is not None
    assert contact.first_name == "Ivan"
    assert fetched.email == "ivan@example.com"


def test_get_contacts_for_user(test_db, fake_user):
    contacts = get_contacts_for_user(test_db, fake_user.id)
    assert isinstance(contacts, list)
    for c in contacts:
        assert c.user_id == fake_user.id


def test_update_contact(test_db: Session, fake_user):
    contact_in = ContactCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        phone_number="987654321",
        birthday="1995-05-05"
    )
    contact = create_contact(test_db, contact_in, fake_user.id)

    update_data = ContactUpdate(
        first_name="Janet",
        phone_number="111222333"
    )
    updated = update_contact(test_db, contact.id, update_data, fake_user.id)
    assert updated.first_name == "Janet"
    assert updated.phone_number == "111222333"


def test_delete_contact(test_db: Session, fake_user):
    contact_in = ContactCreate(
        first_name="ToDelete",
        last_name="Me",
        email="delete@example.com",
        phone_number="000000000",
        birthday="1999-09-09"
    )
    contact = create_contact(test_db, contact_in, fake_user.id)
    deleted = delete_contact(test_db, contact.id, fake_user.id)
    assert deleted is not None
    assert get_contact_by_id(test_db, contact.id, fake_user.id) is None


def test_upcoming_birthdays(test_db: Session, fake_user):
    today = date.today()
    birthday_soon = today + timedelta(days=3)

    contact_in = ContactCreate(
        first_name="Birthday",
        last_name="Soon",
        email="soon@example.com",
        phone_number="333333333",
        birthday=birthday_soon.isoformat()
    )
    create_contact(test_db, contact_in, fake_user.id)

    upcoming = upcoming_birthdays(test_db, fake_user.id)
    assert any(c.email == "soon@example.com" for c in upcoming)


def test_search_contacts(test_db: Session, fake_user):
    contact_in = ContactCreate(
        first_name="Search",
        last_name="Target",
        email="searchme@example.com",
        phone_number="999999999",
        birthday="1980-08-08"
    )
    create_contact(test_db, contact_in, fake_user.id)

    results = search_contacts(test_db, "search", fake_user.id)
    assert any("searchme@example.com" in c.email for c in results)


def test_create_user_and_get_by_email(test_db: Session):
    email = "newuser@example.com"
    user_in = UserCreate(
        username="newuser",
        email=email,
        password="securepassword"
    )
    user = create_user(test_db, user_in)
    assert user.id is not None
    assert user.email == email

    fetched = get_user_by_email(test_db, email)
    assert fetched is not None
    assert fetched.username == "newuser"
