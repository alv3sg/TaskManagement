from pymongo import MongoClient
from .settings import MongoSettings
from datetime import timezone


def get_mongo_client(settings: MongoSettings | None = None) -> MongoClient:
    settings = settings or MongoSettings()
    return MongoClient(settings.uri, retryWrites=True, tz_aware=True, tzinfo=timezone.utc)


def get_db(client: MongoClient, settings: MongoSettings | None = None):
    settings = settings or MongoSettings()
    return client[settings.db_name]
