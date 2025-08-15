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

# ---- Responses ----


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    status: Literal["active", "locked"]
    created_at: datetime
