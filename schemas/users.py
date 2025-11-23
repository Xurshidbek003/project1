from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    google_id: Optional[str] = None


class GoogleAuthRequest(BaseModel):
    token: str