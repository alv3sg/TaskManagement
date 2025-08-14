# app/auth/application/use_cases.py
from __future__ import annotations
from dataclasses import dataclass
from ..domain.entities import User, UserId, Email, PasswordHash, UserStatus
from .ports import UserRepository, PasswordHasher, NotFound, AlreadyExists
import uuid

# Create (Register)


@dataclass
class CreateUser:
    users: UserRepository
    hasher: PasswordHasher

    def execute(self, *, email: str, password: str) -> User:
        email_vo = Email(email)
        if self.users.exists_by_email(email_vo):
            raise AlreadyExists("Email já registrado")
        user = User(
            id=UserId.new(),
            email=email_vo,
            password_hash=PasswordHash(self.hasher.hash(password)),
            status=UserStatus.ACTIVE
        )
        self.users.add(user)
        return user

# Read (Get by id)


@dataclass
class GetUser:
    users: UserRepository

    def execute(self, *, user_id: str) -> User:
        try:
            uid = UserId(uuid.UUID(user_id))
        except Exception:
            raise NotFound("UserId inválido")
        return self.users.get_by_id(uid)

# Read (List)


@dataclass
class ListUsers:
    users: UserRepository

    def execute(self, *, limit: int = 50, offset: int = 0):
        return list(self.users.list(limit=limit, offset=offset))

# Update email


@dataclass
class UpdateUserEmail:
    users: UserRepository

    def execute(self, *, user_id: UserId, new_email: str) -> User:
        user = self.users.get_by_id(user_id)
        email_vo = Email(new_email)
        # regra simples: não permitir duplicados
        # obs: em cenários reais, considerar "exists_by_email && id != user.id"
        try:
            existing = self.users.get_by_email(email_vo)
            if existing.id != user.id:
                raise AlreadyExists("Email já em uso")
        except NotFound:
            pass
        user.change_email(email_vo)
        self.users.save(user)
        return user

# Update password


@dataclass
class UpdateUserPassword:
    users: UserRepository
    hasher: PasswordHasher

    def execute(self, *, user_id: UserId, new_password: str) -> None:
        user = self.users.get_by_id(user_id)
        user.change_password(PasswordHash(self.hasher.hash(new_password)))
        self.users.save(user)

# Update status (lock/unlock)


@dataclass
class SetUserStatus:
    users: UserRepository

    def execute(self, *, user_id: UserId, status: UserStatus) -> None:
        user = self.users.get_by_id(user_id)
        if status == UserStatus.LOCKED:
            user.lock()
        else:
            user.status = UserStatus.ACTIVE
        self.users.save(user)

# Delete (soft delete → lock)


@dataclass
class DeleteUser:
    users: UserRepository

    def execute(self, *, user_id: UserId) -> None:
        user = self.users.get_by_id(user_id)
        user.lock()  # soft delete em auth
        self.users.save(user)
