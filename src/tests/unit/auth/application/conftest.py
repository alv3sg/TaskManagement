import pytest
from collections import OrderedDict
from auth.domain.entities import User, UserId, Email, PasswordHash, UserStatus, RefreshToken
from auth.application.ports import UserRepository, NotFound, RefreshTokenRepository, AccessTokenEncoder, PasswordHasher
from datetime import timedelta, timezone, datetime
from uuid import UUID
# ---- Fakes ----


class FakeUserRepo(UserRepository):
    def __init__(self):
        self._users_by_id: dict[UserId, User] = OrderedDict()
        self._id_by_email: dict[str, UserId] = {}

    def add(self, user: User) -> None:
        self._users_by_id[user.id] = user
        self._id_by_email[user.email.value] = user.id

    def save(self, user: User) -> None:
        if user.id not in self._users_by_id:
            raise NotFound("Usuário não encontrado")
        self._users_by_id[user.id] = user
        self._id_by_email[user.email.value] = user.id

    def get_by_id(self, user_id: UserId) -> User:
        try:
            return self._users_by_id[user_id]
        except KeyError:
            raise NotFound("Usuário não encontrado")

    def get_by_email(self, email: Email) -> User:
        uid = self._id_by_email.get(email.value)
        if not uid:
            raise NotFound("Usuário não encontrado")
        return self._users_by_id[uid]

    def exists_by_email(self, email: Email) -> bool:
        return email.value in self._id_by_email

    def list(self, *, limit: int = 50, offset: int = 0):
        values = list(self._users_by_id.values())
        return values[offset: offset + limit]

    def get_auth_view_by_email(
            self, email: Email) -> tuple[UserId, PasswordHash, str]:
        user = self.get_by_email(email)
        status = user.status.value if hasattr(
            user.status, "value") else user.status
        return (user.id, user.password_hash, status)


class FakeHasher:
    def hash(self, pwd: str) -> str:
        return "hash::" + pwd

    def verify(self, pwd: str, password_hash: str) -> bool:
        return password_hash == "hash::" + pwd


class FakeRefreshTokenRepo:
    def add(self, token: RefreshToken) -> None: ...

    def get(self, token_id: str) -> RefreshToken:
        return RefreshToken(
            id=UUID(token_id),
            user_id=UserId.new(),
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            revoked_at=None
        )

    def save(self, token: RefreshToken) -> None: ...
    def revoke(self, token_id: str) -> None: ...


class FakeAccessTokenEncoder:
    def encode(self, subject: str, ttl: timedelta) -> str:
        return "token::" + subject + "::" + str(ttl)
# ---- Fixtures ----


@pytest.fixture
def user_repo():
    return FakeUserRepo()


@pytest.fixture
def hasher():
    return FakeHasher()


@pytest.fixture
def refresh_repo():
    return FakeRefreshTokenRepo()


@pytest.fixture
def access_tokens():
    return FakeAccessTokenEncoder()


@pytest.fixture
def make_user(user_repo):
    def _mk(email="u@example.com", status=UserStatus.ACTIVE):
        u = User(
            id=UserId.new(),
            email=Email(email),
            password_hash=PasswordHash("hash::secretsecretsecret"),
            status=status,
        )
        user_repo.add(u)
        return u
    return _mk


class FakeHasher:
    def hash(self, pwd: str) -> str:
        # produce a long deterministic string
        return "hash$" + pwd + "$" + ("X"*25)  # length > 20

    def verify(self, pwd: str, password_hash: str) -> bool:
        # mirror the same pattern
        return password_hash == self.hash(pwd)
