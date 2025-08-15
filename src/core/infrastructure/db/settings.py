from dataclasses import dataclass
import os


@dataclass(frozen=True)
class MongoSettings:
    uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name: str = os.getenv("MONGO_DB", "gtd_app")
