import pytest
from auth.application.user_cases import Login, CreateUser, DeleteUser
from auth.application.ports import Unauthorized
from auth.domain.entities import UserId


def test_login_happy_path(user_repo, hasher, refresh_repo, access_tokens):
    # 1) Seed a user using the real use case so hashing/status are correct
    create = CreateUser(users=user_repo, hasher=hasher)
    create.execute(email="New@Example.com", password="hunter2hunter2")

    # 2) Exercise login
    uc = Login(users=user_repo,
               refresh_tokens=refresh_repo,
               hasher=hasher,
               access_tokens=access_tokens)
    result = uc.execute(email="New@Example.com", password="hunter2hunter2")

    # 3) Assertions
    assert result.access_token  # not empty
    assert result.refresh_token  # not empty


def test_login_invalid_credentials(user_repo, hasher, refresh_repo, access_tokens):
    create = CreateUser(users=user_repo, hasher=hasher)
    create.execute(email="New@Example.com", password="hunter2hunter2")
    uc = Login(users=user_repo,
               refresh_tokens=refresh_repo,
               hasher=hasher,
               access_tokens=access_tokens)
    with pytest.raises(Unauthorized):
        uc.execute(email="New@Example.com", password="wrong")


def test_login_user_deleted(user_repo, hasher, refresh_repo, access_tokens):
    create = CreateUser(users=user_repo, hasher=hasher)
    user = create.execute(email="New@Example.com", password="hunter2hunter2")
    delete = DeleteUser(users=user_repo)
    delete.execute(user_id=user.id)
    uc = Login(users=user_repo,
               refresh_tokens=refresh_repo,
               hasher=hasher,
               access_tokens=access_tokens)
    with pytest.raises(Unauthorized):
        uc.execute(email="New@Example.com", password="wrong")


def test_login_user_not_found(user_repo, hasher, refresh_repo, access_tokens):
    uc = Login(users=user_repo,
               refresh_tokens=refresh_repo,
               hasher=hasher,
               access_tokens=access_tokens)
    with pytest.raises(Unauthorized):
        uc.execute(email="new@example.com", password="wrong")
