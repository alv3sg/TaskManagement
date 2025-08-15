import pytest
# <- not app.auth...
from auth.domain.entities import PasswordHash, InvalidPasswordHash


def test_password_hash_accepts_nontrivial():
    h = PasswordHash("x" * 25)
    assert h.value == "x" * 25


@pytest.mark.parametrize("bad", ["", "short", "1234567890123456789"])
def test_password_hash_rejects_too_short(bad):
    with pytest.raises(InvalidPasswordHash):
        PasswordHash(bad)
