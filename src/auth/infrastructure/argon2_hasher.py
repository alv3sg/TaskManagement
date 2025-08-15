from argon2 import PasswordHasher as _Argon2
from argon2.exceptions import VerifyMismatchError
from ..application.ports import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._h = _Argon2()  # defaults sensatos; ajustar se necessário

    def hash(self, password: str) -> str:
        return self._h.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return self._h.verify(password_hash, password)
        except VerifyMismatchError:
            return False
