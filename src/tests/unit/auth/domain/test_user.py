import uuid
import pytest
from auth.domain.entities import (
    User, UserId, Email, PasswordHash, UserStatus, UserLocked
)


def make_user():
    return User(
        id=UserId.new(),
        email=Email("user@example.com"),
        password_hash=PasswordHash("h"*32),
        status=UserStatus.ACTIVE,
    )


def test_user_can_change_email():
    u = make_user()
    u.change_email(Email("new@example.com"))
    assert u.email.value == "new@example.com"


def test_ensure_can_authenticate_raises_when_locked():
    u = make_user()
    u.lock()
    with pytest.raises(UserLocked):
        u.ensure_can_authenticate()


def test_issue_refresh_token_sets_expiry_and_user_id():
    u = make_user()
    rt = u.issue_refresh_token(token_id=uuid.uuid4(
    ), ttl=__import__("datetime").timedelta(days=7))
    assert rt.user_id == u.id
    assert (rt.expires_at - rt.issued_at).days == 7
