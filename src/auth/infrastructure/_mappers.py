from datetime import datetime
from typing import Any, Dict
import uuid

from ..domain.entities import (
    User, UserId, Email, PasswordHash, UserStatus, RefreshToken, Inbox, InboxStatus
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
        "user_id": str(rt.user_id),
        "issued_at": rt.issued_at,
        "expires_at": rt.expires_at,
        "revoked_at": rt.revoked_at,
    }


def refresh_from_doc(doc: Dict[str, Any]) -> RefreshToken:
    return RefreshToken(
        id=uuid.UUID(doc["_id"]),
        user_id=uuid.UUID(doc["user_id"]),
        issued_at=doc["issued_at"],
        expires_at=doc["expires_at"],
        revoked_at=doc.get("revoked_at"),
    )


def inbox_to_doc(inbox: Inbox) -> Dict[str, Any]:
    return {
        "_id": str(inbox.id),
        "user_id": str(inbox.user_id),
        "description": inbox.description,
        "created_at": inbox.created_at,
        "updated_at": inbox.updated_at,
        "status": inbox.status.value,
    }


def inbox_from_doc(doc: Dict[str, Any]) -> Inbox:
    return Inbox(
        id=uuid.UUID(doc["_id"]),
        user_id=uuid.UUID(doc["user_id"]),
        description=doc["description"],
        created_at=doc["created_at"] if isinstance(doc["created_at"], datetime)
        else datetime.fromisoformat(doc["created_at"]),
        updated_at=doc["updated_at"] if isinstance(doc["updated_at"], datetime)
        else datetime.fromisoformat(doc["updated_at"]) if doc["updated_at"] else None,
        status=InboxStatus(doc.get("status", "active")),
    )
