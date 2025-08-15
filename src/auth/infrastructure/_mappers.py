from datetime import datetime
from typing import Any, Dict
import uuid

from ..domain.entities import (
    User, UserId, Email, PasswordHash, UserStatus, RefreshToken
)

# Armazenamos UUIDs como strings e datetimes como BSON datetimes (timezone-aware)


def user_to_doc(user: User) -> Dict[str, Any]:
    return {
        "_id": str(user.id.value),
        "email": user.email.value,
        "password_hash": user.password_hash.value,
        "status": user.status.value,
        "created_at": user.created_at,  # PyMongo salva datetime com timezone
    }


def user_from_doc(doc: Dict[str, Any]) -> User:
    return User(
        id=UserId(uuid.UUID(doc["_id"])),
        email=Email(doc["email"]),
        password_hash=PasswordHash(doc["password_hash"]),
        status=UserStatus(doc.get("status", "active")),
        created_at=doc["created_at"] if isinstance(doc["created_at"], datetime)
        else datetime.fromisoformat(doc["created_at"]),
    )


def refresh_to_doc(rt: RefreshToken) -> Dict[str, Any]:
    return {
        "_id": str(rt.id),
        "user_id": str(rt.user_id.value),
        "issued_at": rt.issued_at,
        "expires_at": rt.expires_at,
        "revoked_at": rt.revoked_at,
    }


def refresh_from_doc(doc: Dict[str, Any]) -> RefreshToken:
    return RefreshToken(
        id=uuid.UUID(doc["_id"]),
        user_id=UserId(uuid.UUID(doc["user_id"])),
        issued_at=doc["issued_at"],
        expires_at=doc["expires_at"],
        revoked_at=doc.get("revoked_at"),
    )
