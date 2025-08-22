from __future__ import annotations
import os

from fastapi import FastAPI
from dotenv import load_dotenv
from .core.infrastructure.db.settings import MongoSettings
from .auth.interfaces.auth_http import router as auth_router
from .auth.interfaces.user_http import router as users_router
from .auth.infrastructure.jwt_access_token import JwtAccessToken
from .core.infrastructure.db.mongodb import get_mongo_client, get_db
from .auth.infrastructure.argon2_hasher import Argon2PasswordHasher
from .auth.infrastructure.mongo_user_repository import MongoUserRepository
from .auth.infrastructure.mongo_refresh_token_repository import MongoRefreshTokenRepository

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="GTD Task Manager")

    # Infra adapters
    client = get_mongo_client(MongoSettings())
    db = get_db(client)
    app.state.user_repo = MongoUserRepository(db["users"])
    app.state.refresh_repo = MongoRefreshTokenRepository(db["refresh_tokens"])
    app.state.hasher = Argon2PasswordHasher()
    app.state.access_tokens = JwtAccessToken()

    # Interfaces
    app.include_router(users_router)
    app.include_router(auth_router)

    return app


app = create_app()
