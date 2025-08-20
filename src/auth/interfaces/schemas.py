from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from uuid import UUID
from datetime import datetime

# ---- Requests ----


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UpdateEmailRequest(BaseModel):
    email: EmailStr


class UpdatePasswordRequest(BaseModel):
    password: str = Field(min_length=8)


class UpdateStatusRequest(BaseModel):
    status: Literal["active", "locked"]


class TokenRefreshRequest(BaseModel):
    refresh_token: str

# ---- Responses ----


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    status: Literal["active", "locked"]
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPairResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
