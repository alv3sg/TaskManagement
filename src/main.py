from __future__ import annotations

from fastapi import FastAPI
from .core.infrastructure.db.mongodb import get_mongo_client, get_db
from .core.infrastructure.db.settings import MongoSettings
from .auth.infrastructure.mongo_user_repository import MongoUserRepository
from .auth.infrastructure.mongo_refresh_token_repository import MongoRefreshTokenRepository
from .auth.infrastructure.argon2_hasher import Argon2PasswordHasher
from .auth.interfaces.http import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="GTD Task Manager")

    # Infra adapters
    client = get_mongo_client(MongoSettings())
    db = get_db(client)
    app.state.user_repo = MongoUserRepository(db["users"])
    app.state.refresh_repo = MongoRefreshTokenRepository(db["refresh_tokens"])
    app.state.hasher = Argon2PasswordHasher()

    # Interfaces
    app.include_router(users_router)

    return app


app = create_app()
