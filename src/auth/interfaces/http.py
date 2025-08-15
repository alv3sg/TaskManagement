from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from uuid import UUID

from .schemas import (
    CreateUserRequest, UpdateEmailRequest, UpdatePasswordRequest,
    UpdateStatusRequest, UserResponse,
)
from ..application.user_cases import (
    CreateUser, GetUser, ListUsers, UpdateUserEmail,
    UpdateUserPassword, SetUserStatus, DeleteUser,
)
from ..application.ports import NotFound, AlreadyExists
from ..domain.entities import UserId, UserStatus

router = APIRouter(prefix="/users", tags=["users"])

# ----- Dependency helpers pulling adapters from app.state -----


def get_user_repo(request: Request):
    return request.app.state.user_repo


def get_hasher(request: Request):
    return request.app.state.hasher

# ----- Mappers (domain -> DTO) -----


def to_user_response(u) -> UserResponse:
    return UserResponse(
        id=u.id.value,
        email=u.email.value,
        status=u.status.value,
        created_at=u.created_at,
    )

# ----- Endpoints -----


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: CreateUserRequest,
    user_repo=Depends(get_user_repo),
    hasher=Depends(get_hasher),
):
    try:
        uc = CreateUser(users=user_repo, hasher=hasher)
        user = uc.execute(email=body.email, password=body.password)
        return to_user_response(user)
    except AlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    user_repo=Depends(get_user_repo),
):
    try:
        uc = GetUser(users=user_repo)
        user = uc.execute(user_id=str(user_id))
        return to_user_response(user)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=list[UserResponse])
def list_users(
    limit: int = 50,
    offset: int = 0,
    user_repo=Depends(get_user_repo),
):
    uc = ListUsers(users=user_repo)
    users = uc.execute(limit=limit, offset=offset)
    return [to_user_response(u) for u in users]


@router.put("/{user_id}/email", response_model=UserResponse)
def update_user_email(
    user_id: UUID,
    body: UpdateEmailRequest,
    user_repo=Depends(get_user_repo),
):
    try:
        uc = UpdateUserEmail(users=user_repo)
        user = uc.execute(user_id=UserId(user_id), new_email=body.email)
        return to_user_response(user)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{user_id}/password", status_code=204)
def update_user_password(
    user_id: UUID,
    body: UpdatePasswordRequest,
    user_repo=Depends(get_user_repo),
    hasher=Depends(get_hasher),
):
    try:
        uc = UpdateUserPassword(users=user_repo, hasher=hasher)
        uc.execute(user_id=UserId(user_id), new_password=body.password)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}/status", status_code=204)
def set_user_status(
    user_id: UUID,
    body: UpdateStatusRequest,
    user_repo=Depends(get_user_repo),
):
    try:
        status_vo = UserStatus(body.status)
        uc = SetUserStatus(users=user_repo)
        uc.execute(user_id=UserId(user_id), status=status_vo)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    user_repo=Depends(get_user_repo),
):
    try:
        uc = DeleteUser(users=user_repo)
        uc.execute(user_id=UserId(user_id))
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
