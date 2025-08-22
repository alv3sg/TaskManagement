import os
from uu import decode
import jwt
from ..application.ports import AccessTokenEncoder, AccessTokenClaims
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


class JwtAccessToken(AccessTokenEncoder):
    def __init__(self, secret: str | None = None, algorithm: str = "HS256", leeway: int = 30):
        self.SECRET_KEY = secret or os.getenv("SECRET_KEY")
        self.ALGORITHM = algorithm
        self.leeway = leeway

    def encode(self, claims: AccessTokenClaims) -> str:
        return jwt.encode(claims, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode(self, token: str) -> AccessTokenClaims:
        # verify signature + exp automatically
        data = jwt.decode(
            token,
            self.SECRET_KEY,
            algorithms=[self.ALGORITHM],
            options={"require": ["exp", "sub", "typ"]},
            leeway=self.leeway,
        )
        if data.get("typ") != "access":
            raise jwt.InvalidTokenError("Wrong token type")
        return data  # type: ignore[return-value]
