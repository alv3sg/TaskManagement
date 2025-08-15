from typing import Iterable
from pymongo.collection import Collection
from pymongo import ASCENDING, ReturnDocument

from ..application.ports import UserRepository, NotFound, AlreadyExists
from ..domain.entities import User, UserId, Email
from ._mappers import user_to_doc, user_from_doc


class MongoUserRepository(UserRepository):
    def __init__(self, col: Collection):
        self.col = col
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.col.create_index([("email", ASCENDING)], unique=True)
        self.col.create_index([("created_at", ASCENDING)])

    def add(self, user: User) -> None:
        try:
            self.col.insert_one(user_to_doc(user))
        except Exception as e:
            msg = str(e).lower()
            if "duplicate key" in msg or "e11000" in msg:
                raise AlreadyExists("Email já registrado") from e
            raise

    def save(self, user: User) -> None:
        doc = user_to_doc(user)
        res = self.col.find_one_and_replace(
            {"_id": doc["_id"]}, doc, return_document=ReturnDocument.AFTER)
        if not res:
            raise NotFound("Usuário não encontrado")

    def get_by_id(self, user_id: UserId) -> User:
        doc = self.col.find_one({"_id": str(user_id.value)})
        if not doc:
            raise NotFound("Usuário não encontrado")
        return user_from_doc(doc)

    def get_by_email(self, email: Email) -> User:
        doc = self.col.find_one({"email": email.value})
        if not doc:
            raise NotFound("Usuário não encontrado")
        return user_from_doc(doc)

    def exists_by_email(self, email: Email) -> bool:
        return self.col.count_documents({"email": email.value}, limit=1) > 0

    def list(self, *, limit: int = 50, offset: int = 0) -> Iterable[User]:
        cursor = (self.col.find({})
                  .sort("created_at", ASCENDING)
                  .skip(offset)
                  .limit(limit))
        for doc in cursor:
            yield user_from_doc(doc)
