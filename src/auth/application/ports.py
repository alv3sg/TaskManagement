# app/auth/application/ports.py
from __future__ import annotations
from typing import Protocol, Iterable, TypedDict
from dataclasses import dataclass
from datetime import timedelta
from ..domain.entities import User, UserId, Email, PasswordHash, RefreshToken


# Erros da aplicação (não HTTP)


class NotFound(Exception):
    ...


class AlreadyExists(Exception):
    ...


class Unauthorized(Exception):
    ...


class UserRepository(Protocol):
    def add(self, user: User) -> None: ...
    def save(self, user: User) -> None: ...
    def get_by_id(self, user_id: UserId) -> User: ...
    def get_by_email(self, email: Email) -> User: ...
    def exists_by_email(self, email: Email) -> bool: ...
    def list(self, *, limit: int = 50, offset: int = 0) -> Iterable[User]: ...
    def get_auth_view_by_email(
        self, email: Email) -> tuple[UserId, PasswordHash, str]: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, password_hash: str) -> bool: ...


class RefreshTokenRepository(Protocol):
    def add(self, token: RefreshToken) -> None: ...
    def get(self, token_id: str) -> RefreshToken: ...
    def save(self, token: RefreshToken) -> None: ...
    def revoke(self, token_id: str) -> None: ...


class AccessTokenClaims(TypedDict):
    sub: str          # user id
    exp: int          # unix timestamp
    scope: str        # e.g. "user", "admin", "user:read user:write"
    typ: str          # "access"


class AccessTokenEncoder(Protocol):
    def encode(self, subject: str, ttl: timedelta) -> str: ...
    def decode(self, token: str) -> AccessTokenClaims: ...


@dataclass
class LoginResult:
    user_id: UserId
    access_token: str
    refresh_token: str  # or a VO if you prefer
