from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
import re
import uuid


class DomainError(Exception):
    pass


class UserLocked(DomainError):
    pass


class TokenExpired(DomainError):
    pass


class InvalidEmail(DomainError):
    pass


class InvalidPasswordHash(DomainError):
    pass


_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        normalized = self.value.strip().lower()
        if not _EMAIL_REGEX.match(normalized):
            raise InvalidEmail("Email inválido")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class UserId:
    value: uuid.UUID

    @staticmethod
    def new() -> "UserId":
        return UserId(uuid.uuid4())


@dataclass(frozen=True)
class PasswordHash:
    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 20:
            raise InvalidPasswordHash("Hash de senha inválido")


class UserStatus(str, Enum):
    ACTIVE = "active"
    LOCKED = "locked"


@dataclass
class User:
    id: UserId
    email: Email
    password_hash: PasswordHash
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    def change_email(self, new_email: Email) -> None:
        self.email = new_email

    def change_password(self, new_password_hash: PasswordHash) -> None:
        self.password_hash = new_password_hash

    def ensure_can_authenticate(self) -> None:
        if self.status != UserStatus.ACTIVE:
            raise UserLocked("Usuário bloqueado")

    def lock(self) -> None:
        self.status = UserStatus.LOCKED

    def issue_refresh_token(
        self,
        token_id: uuid.UUID,
        ttl: timedelta,
        now: datetime | None = None
    ) -> RefreshToken:
        self.ensure_can_authenticate()
        now = now or datetime.now(timezone.utc)
        return RefreshToken(
            id=token_id,
            user_id=self.id,
            issued_at=now,
            expires_at=now + ttl,
            revoked_at=None
        )


@dataclass
class RefreshToken:
    id: uuid.UUID
    user_id: UserId
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None

    def ensure_active(self, at: datetime | None = None) -> None:
        at = at or datetime.now(timezone.utc)
        if self.revoked_at is not None or at >= self.expires_at:
            raise TokenExpired("Refresh token expirado ou revogado.")

    def revoke(self, at: datetime | None = None) -> None:
        if self.revoked_at is None:
            self.revoked_at = at or datetime.now(timezone.utc)
