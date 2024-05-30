import os
import logging
import pymongo

logger = logging.getLogger(__name__)
DATABASE = os.environ.get("DATABASE", "ai-e2e-boilerplate")
HOST = os.environ.get("HOST", "mongo")
PORT = os.environ.get("PORT", 27017)

class MongoConnector:
    def __init__(self) -> None:
        self.client = None
        self.db = None

    def connect(self) -> None:
        if self.db is None:
            logger.info("Initializing connection to the database...")
            self.client = pymongo.MongoClient(f"mongodb://{HOST}:{PORT}")
            self.db = self.client[DATABASE]

    def disconnect(self) -> None:
        if self.connection is not None:
            self.connection.close()

db_client = MongoConnector()
db_client.connect()
db = db_client.db
logger.info(f"Initializing connection to the database...")
