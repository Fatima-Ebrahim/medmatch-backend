from pydantic import BaseModel, EmailStr
from typing import Literal

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Literal["mentee", "mentor", "investigator", "admin"]

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    # Never return password_hash

    class Config:
        from_attributes = True