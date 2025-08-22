from typing import Iterable
from pymongo.collection import Collection
from pymongo import ASCENDING, ReturnDocument

from ..application.ports import InboxRepository, NotFound
from ..domain.entities import Inbox, UserId
from ._mappers import inbox_to_doc, inbox_from_doc


class MongoInboxRepository(InboxRepository):
    def __init__(self, col: Collection):
        self.col = col
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.col.create_index([("user_id", ASCENDING)])
        self.col.create_index([("created_at", ASCENDING)])

    def add(self, inbox: Inbox) -> None:
        try:
            self.col.insert_one(inbox_to_doc(inbox))
        except Exception as e:
            raise e

    def save(self, inbox: Inbox) -> None:
        doc = inbox_to_doc(inbox)
        res = self.col.find_one_and_replace(
            {"_id": doc["_id"]}, doc, return_document=ReturnDocument.AFTER)
        if not res:
            raise NotFound("Inbox não encontrado")

    def get_by_inbox_id(self, inbox_id: str) -> Inbox:
        doc = self.col.find_one({"_id": inbox_id})
        if not doc:
            raise NotFound("Inbox não encontrado")
        return inbox_from_doc(doc)

    def get_by_user_id(self, *, user_id: str, limit: int = 50, offset: int = 0) -> Iterable[Inbox]:
        cursor = self.col.find({"user_id": user_id})
        for doc in cursor:
            yield inbox_from_doc(doc)

    def list(self, *, limit: int = 50, offset: int = 0) -> Iterable[Inbox]:
        cursor = (self.col.find({})
                  .sort("created_at", ASCENDING)
                  .skip(offset)
                  .limit(limit))
        for doc in cursor:
            yield inbox_from_doc(doc)
