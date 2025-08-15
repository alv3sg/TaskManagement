from auth.application.user_cases import UpdateUserPassword


def test_update_user_password(user_repo, hasher, make_user):
    u = make_user(email="pw@example.com")
    old = u.password_hash.value
    uc = UpdateUserPassword(users=user_repo, hasher=hasher)
    uc.execute(user_id=u.id, new_password="newpassssss")
    got = user_repo.get_by_id(u.id)
    assert got.password_hash.value != old
    assert got.password_hash.value == hasher.hash("newpassssss")
