from pymongo.collection import Collection
from pymongo import ASCENDING, ReturnDocument

from ..application.ports import RefreshTokenRepository, NotFound
from ..domain.entities import RefreshToken
from ._mappers import refresh_to_doc, refresh_from_doc


class MongoRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, col: Collection):
        self.col = col
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.col.create_index([("user_id", ASCENDING)])
        self.col.create_index([("revoked_at", ASCENDING)])
        self.col.create_index([("expires_at", ASCENDING)])

    def add(self, token: RefreshToken) -> None:
        self.col.insert_one(refresh_to_doc(token))

    def get(self, token_id: str) -> RefreshToken:
        doc = self.col.find_one({"_id": token_id})
        if not doc:
            raise NotFound("Refresh token não encontrado")
        return refresh_from_doc(doc)

    def save(self, token: RefreshToken) -> None:
        doc = refresh_to_doc(token)
        res = self.col.find_one_and_replace(
            {"_id": doc["_id"]}, doc, return_document=ReturnDocument.AFTER)
        if not res:
            raise NotFound("Refresh token não encontrado")

    # útil para logout global (opcional, controlado pelo use case)
    def revoke_all_for_user(self, user_id: str, now) -> int:
        res = self.col.update_many(
            {"user_id": user_id, "revoked_at": None},
            {"$set": {"revoked_at": now}}
        )
        return res.modified_count
