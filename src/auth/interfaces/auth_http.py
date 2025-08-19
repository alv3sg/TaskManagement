# auth/interfaces/auth_http.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from datetime import timedelta
from .schemas import LoginRequest, TokenPairResponse
from ..application.user_cases import Login
from ..application.ports import Unauthorized

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_repo(request: Request):
    return request.app.state.user_repo


def get_refresh_repo(request: Request):
    return request.app.state.refresh_repo


def get_hasher(request: Request):
    return request.app.state.hasher


def get_access_tokens(request: Request):
    return request.app.state.access_tokens


@router.post("/login", response_model=TokenPairResponse)
def login(
    body: LoginRequest,
    user_repo=Depends(get_user_repo),
    refresh_repo=Depends(get_refresh_repo),
    hasher=Depends(get_hasher),
    access_tokens=Depends(get_access_tokens),
):
    uc = Login(
        users=user_repo,
        refresh_tokens=refresh_repo,
        hasher=hasher,
        access_tokens=access_tokens,
        access_ttl=timedelta(minutes=30),
        refresh_ttl=timedelta(days=7),
    )
    try:
        result = uc.execute(email=body.email, password=body.password)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return {
        "access_token": result.access_token,
        "token_type": "bearer",
        "refresh_token": result.refresh_token,
    }
