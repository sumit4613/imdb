from typing import Optional

from pydantic import BaseModel, EmailStr
from pydantic.schema import datetime
from pydantic.types import UUID


# Shared properties
class UserBase(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    full_name = str
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
