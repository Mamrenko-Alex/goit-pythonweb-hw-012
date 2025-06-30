import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from models import User
import schemas
import pytest
from jose import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = "HS256"


def create_token(user_id: int) -> str:
    token = jwt.encode({"sub": str(user_id)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


def test_create_contact_success(client, test_db, fake_user):
    contact_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "phone_number": "123456789",
        "birthday": "1990-01-01"
    }

    response = client.post(
        "/contacts/", json=contact_data, headers=create_token(fake_user))
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["first_name"] == "Test"


# def test_read_contact_success(client, test_db, fake_user):
#     # Спочатку створюємо контакт
#     contact_data = {
#         "first_name": "Read",
#         "last_name": "Contact",
#         "email": "readcontact@example.com",
#         "phone_number": "987654321",
#         "birthday": "1985-05-05"
#     }
#     response_create = client.post("/contacts/", json=contact_data)
#     contact_id = response_create.json()["id"]

#     response = client.get(f"/contacts/{contact_id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["email"] == "readcontact@example.com"


# def test_read_contact_not_found(client):
#     response = client.get("/contacts/999999")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Контакт не знайдено"


# def test_update_contact_success(client, test_db, fake_user):
#     contact_data = {
#         "first_name": "Update",
#         "last_name": "Me",
#         "email": "updateme@example.com",
#         "phone_number": "555555555",
#         "birthday": "1999-09-09"
#     }
#     response_create = client.post("/contacts/", json=contact_data)
#     contact_id = response_create.json()["id"]

#     update_data = {
#         "first_name": "Updated",
#         "phone_number": "111222333"
#     }
#     response_update = client.put(f"/contacts/{contact_id}", json=update_data)
#     assert response_update.status_code == 200
#     data = response_update.json()
#     assert data["first_name"] == "Updated"
#     assert data["phone_number"] == "111222333"


# def test_update_contact_not_found(client):
#     update_data = {
#         "first_name": "Nobody"
#     }
#     response = client.put("/contacts/999999", json=update_data)
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Контакт не знайдено"


# def test_delete_contact_success(client, test_db, fake_user):
#     contact_data = {
#         "first_name": "Delete",
#         "last_name": "Me",
#         "email": "deleteme@example.com",
#         "phone_number": "000000000",
#         "birthday": "1990-01-01"
#     }
#     response_create = client.post("/contacts/", json=contact_data)
#     contact_id = response_create.json()["id"]

#     response_delete = client.delete(f"/contacts/{contact_id}")
#     assert response_delete.status_code == 200
#     assert response_delete.json() == {"ok": True}


# def test_delete_contact_not_found(client):
#     response = client.delete("/contacts/999999")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Контакт не знайдено"


# def test_search_contacts(client, test_db, fake_user):
#     # Створюємо контакт, щоб потім знайти його
#     contact_data = {
#         "first_name": "Search",
#         "last_name": "Target",
#         "email": "searchtarget@example.com",
#         "phone_number": "999999999",
#         "birthday": "1980-08-08"
#     }
#     client.post("/contacts/", json=contact_data)

#     response = client.get("/search/", params={"query": "search"})
#     assert response.status_code == 200
#     results = response.json()
#     assert any("searchtarget@example.com" == c["email"] for c in results)


# def test_birthdays(client, test_db, fake_user):
#     response = client.get("/birthdays/")
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)


# def test_read_current_user(client, fake_user):
#     response = client.get("/me")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["email"] == fake_user.email


# @patch("services.cloudinary_service.upload_avatar", return_value="http://avatar.url/image.png")
# def test_update_avatar(mock_upload_avatar, client, fake_user):
#     # Імітуємо файл
#     file_content = b"fakeimagecontent"
#     files = {"file": ("avatar.png", file_content, "image/png")}

#     response = client.post("/me/avatar", files=files)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["avatar_url"] == "http://avatar.url/image.png"
#     mock_upload_avatar.assert_called_once()
