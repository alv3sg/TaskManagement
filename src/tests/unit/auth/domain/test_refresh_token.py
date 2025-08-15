from datetime import datetime, timedelta, timezone
import uuid
import pytest
from auth.domain.entities import RefreshToken, UserId, TokenExpired


def make_rt(now=None, ttl=timedelta(days=7)):
    now = now or datetime.now(timezone.utc)
    return RefreshToken(
        id=uuid.uuid4(),
        user_id=UserId.new(),
        issued_at=now,
        expires_at=now + ttl,
        revoked_at=None,
    )


def test_refresh_token_active_then_expired():
    now = datetime.now(timezone.utc)
    rt = make_rt(now=now, ttl=timedelta(minutes=1))
    # Active now
    rt.ensure_active(at=now + timedelta(seconds=30))
    # Expired later
    with pytest.raises(TokenExpired):
        rt.ensure_active(at=now + timedelta(minutes=2))


def test_revoke_sets_revoked_at_and_blocks():
    rt = make_rt()
    rt.revoke()
    with pytest.raises(TokenExpired):
        rt.ensure_active()
