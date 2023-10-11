from pymongo import MongoClient


class mongoClient:
    def __init__(self, db_server: str):
        self.client = MongoClient(db_server, serverSelectionTimeoutMS=5000)
        self.db = self.client["Boch"]
        self.collection_auth = self.db["Auth"]

    def close_client(self):
        self.client.close()
