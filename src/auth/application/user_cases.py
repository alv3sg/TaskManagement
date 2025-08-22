# app/auth/application/use_cases.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4, UUID
from ..domain.entities import User, UserId, Email, PasswordHash, UserStatus, TokenExpired, Inbox
from .ports import UserRepository, PasswordHasher, NotFound, AlreadyExists, RefreshTokenRepository, AccessTokenEncoder, Unauthorized, LoginResult, AccessTokenClaims, InboxRepository
from datetime import datetime, timezone


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
            uid = UserId(UUID(user_id))
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


@dataclass
class Login:
    users: UserRepository
    refresh_tokens: RefreshTokenRepository
    hasher: PasswordHasher
    access_tokens: AccessTokenEncoder
    access_ttl: timedelta = timedelta(minutes=30)
    refresh_ttl: timedelta = timedelta(days=7)

    def execute(self, *, email: str, password: str) -> LoginResult:
        email_vo = Email(email)

        try:
            user_id, pwd_hash, status = self.users.get_auth_view_by_email(
                email_vo)
        except NotFound:
            raise Unauthorized("Invalid credentials.")

        if status != UserStatus.ACTIVE.value:
            raise Unauthorized("Invalid credentials.")

        if not self.hasher.verify(password, pwd_hash.value):
            raise Unauthorized("Invalid credentials.")

        user = self.users.get_by_id(user_id)
        refresh = user.issue_refresh_token(
            token_id=uuid4(), ttl=self.refresh_ttl)
        self.refresh_tokens.add(refresh)

        access = self.access_tokens.encode(
            AccessTokenClaims(
                sub=str(user_id.value),
                exp=datetime.now(timezone.utc) + self.access_ttl,
                iat=datetime.now(timezone.utc),
                jti=str(uuid4()),
                typ="access",
            )
        )

        return LoginResult(user_id=user_id, access_token=access, refresh_token=str(refresh.id))


@dataclass
class CreateNewAccessToken:
    refresh_tokens: RefreshTokenRepository
    access_tokens: AccessTokenEncoder
    access_ttl: timedelta = timedelta(minutes=30)
    refresh_ttl: timedelta = timedelta(days=7)

    def execute(self, *, refresh_token: str) -> LoginResult:
        try:
            refresh = self.refresh_tokens.get(refresh_token)
        except NotFound:
            raise Unauthorized("Invalid refresh token.")
        try:
            refresh.ensure_active(datetime.now(timezone.utc))
        except TokenExpired:
            raise Unauthorized("Invalid refresh token.")
        access = self.access_tokens.encode(
            AccessTokenClaims(
                sub=str(refresh.user_id),
                exp=datetime.now(timezone.utc) + self.access_ttl,
                iat=datetime.now(timezone.utc),
                jti=str(uuid4()),
                typ="access",
            )
        )
        return LoginResult(user_id=refresh.user_id, access_token=access, refresh_token=str(refresh.id))


@dataclass
class Logout:
    refresh_tokens: RefreshTokenRepository

    def execute(self, *, refresh_token: str):
        try:
            refresh = self.refresh_tokens.get(refresh_token)
        except NotFound:
            raise Unauthorized("Invalid refresh token.")
        try:
            refresh.revoke()
            self.refresh_tokens.save(refresh)
        except TokenExpired:
            raise Unauthorized("Invalid refresh token.")


@dataclass
class CreateInbox:
    users: UserRepository
    inboxes: InboxRepository

    def execute(self, *, user_id: str, description: str) -> Inbox:
        try:
            user = self.users.get_by_id(UserId(user_id))
            inbox = user.issue_inbox(description)
            self.inboxes.add(inbox)
            return inbox
        except (ValueError, AttributeError) as e:
            if "badly formed hexadecimal UUID string" in str(e):
                raise ValueError(f"Invalid user ID format: {user_id}")
            raise


@dataclass
class ListInboxes:
    inboxes: InboxRepository

    def execute(self, *, limit: int = 50, offset: int = 0) -> list[Inbox]:
        try:
            return list(self.inboxes.list(limit=limit, offset=offset))
        except NotFound:
            raise ValueError(f"Inbox not found")


@dataclass
class GetInbox:
    inboxes: InboxRepository

    def execute(self, *, inbox_id: str) -> Inbox:
        try:
            return self.inboxes.get_by_inbox_id(inbox_id)
        except NotFound:
            raise ValueError(f"Inbox not found")


@dataclass
class GetInboxByUserId:
    inboxes: InboxRepository

    def execute(self, *, user_id: str, limit: int = 50, offset: int = 0) -> list[Inbox]:
        try:
            return list(self.inboxes.get_by_user_id(user_id=user_id, limit=limit, offset=offset))
        except NotFound:
            raise ValueError(f"Inbox not found")


@dataclass
class UpdateInbox:
    inboxes: InboxRepository

    def execute(self, *, inbox_id: str, description: str) -> Inbox:
        try:
            inbox = self.inboxes.get_by_inbox_id(inbox_id)
            if not inbox:
                raise ValueError(f"Inbox not found")
            inbox.update(description)
            self.inboxes.save(inbox)
            return inbox
        except NotFound:
            raise ValueError(f"Inbox not found")


@dataclass
class DeleteInbox:
    inboxes: InboxRepository

    def execute(self, *, inbox_id: str) -> Inbox:
        try:
            inbox = self.inboxes.get_by_inbox_id(inbox_id)
            if not inbox:
                raise ValueError(f"Inbox not found")
            inbox.delete()
            self.inboxes.save(inbox)
            return inbox
        except NotFound:
            raise ValueError(f"Inbox not found")


@dataclass
class MoveInbox:
    inboxes: InboxRepository

    def execute(self, *, inbox_id: str) -> Inbox:
        try:
            inbox = self.inboxes.get_by_inbox_id(inbox_id)
            if not inbox:
                raise ValueError(f"Inbox not found")
            inbox.move()
            self.inboxes.save(inbox)
            return inbox
        except NotFound:
            raise ValueError(f"Inbox not found")
