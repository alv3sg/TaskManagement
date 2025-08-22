from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import InboxRequest
from ..application.user_cases import CreateInbox, ListInboxes, GetInbox, GetInboxByUserId, UpdateInbox, DeleteInbox, MoveInbox
from fastapi.security import OAuth2PasswordBearer
from .dependences import require_auth, CurrentUser, get_user_repo, get_inbox_repo

router = APIRouter(prefix="/inboxes", tags=["inboxes"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_auth)])
def create_inbox(
    body: InboxRequest,
    user_repo=Depends(get_user_repo),
    inbox_repo=Depends(get_inbox_repo),
    cu: CurrentUser = Depends(require_auth),
):
    try:
        uc = CreateInbox(users=user_repo, inboxes=inbox_repo)
        inbox = uc.execute(user_id=cu.user_id, description=body.description)
        return inbox
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", dependencies=[Depends(require_auth)])
def list_inboxes(
    limit: int = 50,
    offset: int = 0,
    user_repo=Depends(get_user_repo),
    inbox_repo=Depends(get_inbox_repo),
    cu: CurrentUser = Depends(require_auth),
):
    try:
        uc = ListInboxes(inboxes=inbox_repo)
        inboxes = uc.execute(limit=limit, offset=offset)
        return inboxes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{inbox_id}", dependencies=[Depends(require_auth)])
def get_inbox_by_inbox_id(
    inbox_id: str,
    user_repo=Depends(get_user_repo),
    inbox_repo=Depends(get_inbox_repo),
    cu: CurrentUser = Depends(require_auth),
):
    try:
        uc = GetInbox(inboxes=inbox_repo)
        inbox = uc.execute(inbox_id=inbox_id)
        return inbox
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by_user/{user_id}", dependencies=[Depends(require_auth)])
def get_inbox_by_user_id(
    user_id: str,
    user_repo=Depends(get_user_repo),
    inbox_repo=Depends(get_inbox_repo),
    cu: CurrentUser = Depends(require_auth),
):
    if user_id != str(cu.user_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    try:
        uc = GetInboxByUserId(inboxes=inbox_repo)
        inboxes = uc.execute(user_id=user_id, limit=50, offset=0)
        return inboxes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{inbox_id}/description", dependencies=[Depends(require_auth)])
def update_inbox_by_inbox_id(
    inbox_id: str,
    body: InboxRequest,
    user_repo=Depends(get_user_repo),
    inbox_repo=Depends(get_inbox_repo),
    cu: CurrentUser = Depends(require_auth),
):

    try:
        uc = UpdateInbox(inboxes=inbox_repo)
        inbox = uc.execute(inbox_id=inbox_id, description=body.description)
        return inbox
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{inbox_id}/move", dependencies=[Depends(require_auth)])
def move_inbox_by_inbox_id(
    inbox_id: str,
    user_repo=Depends(get_user_repo),
    inbox_repo=Depends(get_inbox_repo),
    cu: CurrentUser = Depends(require_auth),
):

    try:
        uc = MoveInbox(inboxes=inbox_repo)
        inbox = uc.execute(inbox_id=inbox_id)
        return inbox
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{inbox_id}", dependencies=[Depends(require_auth)])
def delete_inbox_by_inbox_id(
    inbox_id: str,
    user_repo=Depends(get_user_repo),
    inbox_repo=Depends(get_inbox_repo),
    cu: CurrentUser = Depends(require_auth),
):

    try:
        uc = DeleteInbox(inboxes=inbox_repo)
        inbox = uc.execute(inbox_id=inbox_id)
        return inbox
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
