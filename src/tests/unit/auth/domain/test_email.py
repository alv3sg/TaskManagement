from auth.domain.entities import Email, InvalidEmail
import pytest


def test_email_normalizes_and_validates():
    e = Email("  Foo.Bar@Example.COM ")
    assert e.value == "foo.bar@example.com"


@pytest.mark.parametrize("bad", ["", " ", "no-at.com", "a@b", "a@b.", "@x.com"])
def test_email_rejects_invalid(bad):
    with pytest.raises(InvalidEmail):
        Email(bad)
