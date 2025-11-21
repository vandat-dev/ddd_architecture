from typing import Optional, List

from pydantic import BaseModel, Field

from app.constant.enums import UserRole


class LoginSchema(BaseModel):
    email: str
    password: str


class RegisterSchema(BaseModel):
    email: str
    fullname: str
    username: str
    password: str
    phone_number: str
    role: Optional[UserRole] = None


class UserUpdateSchema(BaseModel):
    fullname: str | None = None
    phone_number: str | None = None
    username: str | None = None
    password: str | None = None


class UserFilterSchema(BaseModel):
    fullname: Optional[str] = None
    phone_number: Optional[str] = None
    username: Optional[str] = None


class UserDeleteSchema(BaseModel):
    data: List[dict] = Field(examples=[[{"id": "550e8400-e29b-41d4-a716-446655440000", "is_active": False},
                                        {"id": "550e8400-e29b-41d4-a716-446655440001", "is_active": False}]])
