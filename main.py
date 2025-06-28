from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from models import User
import schemas
import crud
from database import SessionLocal, engine, Base
from routes.auth import router
from dependencies import get_current_user
from fastapi.middleware.cors import CORSMiddleware
from services.cloudinary_service import upload_avatar


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Контактна Книга API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/contacts/", response_model=schemas.ContactResponse)
def create_contact(contact: schemas.ContactCreate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return crud.create_contact(db, contact, current_user.id)


@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_contact(contact_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    contact = crud.get_contact_by_id(db, contact_id, current_user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    return contact


@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, contact: schemas.ContactUpdate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    updated = crud.update_contact(db, contact_id, contact, current_user.id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    return updated


@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    deleted = crud.delete_contact(db, contact_id, current_user.id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    return {"ok": True}


@app.get("/search/", response_model=List[schemas.ContactResponse])
def search(query: str,
           db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    return crud.search_contacts(db, query, current_user.id)


@app.get("/birthdays/", response_model=List[schemas.ContactResponse])
def birthdays(db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    return crud.upcoming_birthdays(db, current_user.id)


@app.get("/me", response_model=schemas.UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/me/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    url = upload_avatar(await file.read())
    current_user.avatar_url = url
    db.commit()
    db.refresh(current_user)
    return {"avatar_url": url}
