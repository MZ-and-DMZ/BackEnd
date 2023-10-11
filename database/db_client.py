from pymongo import MongoClient


class mongoClient:
    def __init__(self, db_server: str):
        self.client = MongoClient(db_server, serverSelectionTimeoutMS=5000)
        self.db = self.client["Boch"]
        self.collection_auth = self.db["Auth"]
        self.collection_users = self.db["Users"]
        self.collection_position = self.db["Position"]

    def close_client(self):
        self.client.close()
