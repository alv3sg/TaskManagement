from auth.application.user_cases import SetUserStatus, DeleteUser
from auth.domain.entities import UserStatus


def test_set_user_status_lock_unlock(user_repo, make_user):
    u = make_user(email="st@example.com")
    uc = SetUserStatus(users=user_repo)
    uc.execute(user_id=u.id, status=UserStatus.LOCKED)
    assert user_repo.get_by_id(u.id).status == UserStatus.LOCKED
    uc.execute(user_id=u.id, status=UserStatus.ACTIVE)
    assert user_repo.get_by_id(u.id).status == UserStatus.ACTIVE


def test_delete_user_soft_lock(user_repo, make_user):
    u = make_user(email="del@example.com")
    uc = DeleteUser(users=user_repo)
    uc.execute(user_id=u.id)
    assert user_repo.get_by_id(u.id).status == UserStatus.LOCKED
