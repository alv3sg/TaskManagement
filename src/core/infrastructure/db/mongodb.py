from pymongo import MongoClient
from .settings import MongoSettings


def get_mongo_client(settings: MongoSettings | None = None) -> MongoClient:
    settings = settings or MongoSettings()
    return MongoClient(settings.uri, retryWrites=True)


def get_db(client: MongoClient, settings: MongoSettings | None = None):
    settings = settings or MongoSettings()
    return client[settings.db_name]
