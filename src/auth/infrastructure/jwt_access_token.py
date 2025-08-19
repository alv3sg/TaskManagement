import os
from datetime import datetime, timedelta, timezone
import jwt
from ..application.ports import AccessTokenEncoder


class JwtAccessToken(AccessTokenEncoder):
    def __init__(self, secret: str | None = None, algorithm: str = "HS256"):
        self.SECRET_KEY = secret or os.getenv("SECRET_KEY")
        self.ALGORITHM = algorithm

    def encode(self, subject: str, ttl: timedelta) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int((now + ttl).timestamp()),
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
