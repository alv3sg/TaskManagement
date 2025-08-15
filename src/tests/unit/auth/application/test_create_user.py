import pytest
from auth.application.user_cases import CreateUser
from auth.application.ports import AlreadyExists


def test_create_user_happy_path(user_repo, hasher):
    uc = CreateUser(users=user_repo, hasher=hasher)
    user = uc.execute(email="New@Example.com", password="hunter2hunter2")
    assert user.email.value == "new@example.com"
    # ensure stored
    got = user_repo.get_by_email(user.email)
    assert got.id == user.id


def test_create_user_rejects_duplicate_email(user_repo, hasher):
    uc = CreateUser(users=user_repo, hasher=hasher)
    uc.execute(email="dupe@example.com", password="secretsecret")
    with pytest.raises(AlreadyExists):
        uc.execute(email="Dupe@Example.com", password="anothersecret")
