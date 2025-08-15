import pytest
from auth.application.user_cases import UpdateUserEmail
from auth.application.ports import AlreadyExists, NotFound
from auth.domain.entities import UserId


def test_update_user_email_ok(user_repo, make_user):
    u = make_user(email="a@example.com")
    uc = UpdateUserEmail(users=user_repo)
    updated = uc.execute(user_id=u.id, new_email="b@example.com")
    assert updated.email.value == "b@example.com"


def test_update_user_email_conflict(user_repo, make_user):
    u1 = make_user(email="a@example.com")
    u2 = make_user(email="b@example.com")
    uc = UpdateUserEmail(users=user_repo)
    with pytest.raises(AlreadyExists):
        uc.execute(user_id=u1.id, new_email="b@example.com")


def test_update_user_email_not_found(user_repo):
    uc = UpdateUserEmail(users=user_repo)
    with pytest.raises(NotFound):
        uc.execute(user_id=UserId.new(), new_email="x@example.com")
