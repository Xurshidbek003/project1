from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import database
from models.users import User
from schemas.users import UserCreate, UserUpdate, UserRead, GoogleAuthRequest
from utils.auth import (
    get_current_user,
    hash_password,
    verify_password,
    create_access_token, verify_google_token,
)
import os



router = APIRouter()


@router.post("/register", status_code=201)
def sign_up(user_data: UserCreate, db: Session = Depends(database)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if user:
        raise HTTPException(400, "User already exists")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"detail": "User created successfully"}


@router.post("/google")
def google_auth(auth_data: GoogleAuthRequest, db: Session = Depends(database)):

    idinfo = verify_google_token(auth_data.token)

    email = idinfo.get('email')
    google_id = idinfo.get('sub')

    if not email:
        raise HTTPException(400,"Email not provided by Google")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        username = email.split('@')[0]

        counter = 1
        original_username = username
        while db.query(User).filter(User.username == username).first():
            username = f"{original_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(os.urandom(32).hex()),
            role="user",
            google_id=google_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if not user.google_id:
            user.google_id = google_id
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "is_new_user": user.google_id == google_id
    }


@router.post("/login")
def sign_in(db: Session = Depends(database), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(401, "User not found")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect password")

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


@router.get("/me", response_model=UserRead)
def profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me")
def update_user(user_data: UserUpdate,db: Session = Depends(database),
                current_user: User = Depends(get_current_user)):

    user = db.query(User).filter(User.id == current_user.id).first()

    if user_data.username:
        user.username = user_data.username

    if user_data.email:
        exists = db.query(User).filter(User.email == user_data.email).first()
        if exists and exists.id != current_user.id:
            raise HTTPException(400, "Email already in use")
        user.email = user_data.email

    if user_data.password:
        user.hashed_password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return {"msg": "User updated successfully"}


@router.delete("/me")
def delete_user(current_user: User = Depends(get_current_user), db: Session = Depends(database)):
    db.query(User).filter(User.id == current_user.id).delete()
    db.commit()
    return {"msg": "User deleted successfully"}
