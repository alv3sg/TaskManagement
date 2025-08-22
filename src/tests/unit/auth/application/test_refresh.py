import pytest
from auth.application.user_cases import Login, CreateUser, CreateNewAccessToken
from auth.application.ports import Unauthorized


def test_refresh_happy_path(user_repo, hasher, refresh_repo, access_tokens):
    # 1) Seed a user using the real use case so hashing/status are correct
    create = CreateUser(users=user_repo, hasher=hasher)
    create.execute(email="New@Example.com", password="hunter2hunter2")

    # 2) Exercise login
    uc = Login(users=user_repo,
               refresh_tokens=refresh_repo,
               hasher=hasher,
               access_tokens=access_tokens)
    result = uc.execute(email="New@Example.com", password="hunter2hunter2")

    # 3) Exercise refresh
    refresh = CreateNewAccessToken(
        refresh_tokens=refresh_repo, access_tokens=access_tokens)
    result = refresh.execute(refresh_token=result.refresh_token)

    # 4) Assertions
    assert result.access_token  # not empty
    assert result.refresh_token  # not empty


def test_refresh_invalid_token(refresh_repo, access_tokens):
    refresh = CreateNewAccessToken(
        refresh_tokens=refresh_repo, access_tokens=access_tokens)
    with pytest.raises(Unauthorized):
        refresh.execute(refresh_token="invalid")
