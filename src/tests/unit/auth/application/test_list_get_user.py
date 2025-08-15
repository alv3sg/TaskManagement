from auth.application.user_cases import ListUsers, GetUser
from auth.application.ports import NotFound


def test_list_users(user_repo, make_user):
    make_user(email="a@example.com")
    make_user(email="b@example.com")
    uc = ListUsers(users=user_repo)
    items = uc.execute(limit=10, offset=0)
    assert len(items) == 2


def test_get_user_by_id(user_repo, make_user):
    u = make_user(email="x@example.com")
    uc = GetUser(users=user_repo)
    got = uc.execute(user_id=str(u.id.value))
    assert got.id == u.id


def test_get_user_not_found(user_repo):
    uc = GetUser(users=user_repo)
    import uuid
    bogus = str(uuid.uuid4())
    try:
        uc.execute(user_id=bogus)
        assert False, "expected NotFound"
    except NotFound:
        pass
