from pydantic import BaseModel, EmailStr
from typing import Optional

# Base schema for user attributes
class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phone: Optional[str] = None
    username: str

# Schema for creating a user (inherits from UserBase)
class UserCreate(UserBase):
    pass

# Schema for updating a user (all fields optional)
class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    username: Optional[str] = None

# Schema for reading a user (includes id, inherits from UserBase)
class User(UserBase):
    id: int

    class Config:
        from_attributes = True # Renamed from orm_mode in Pydantic v2
