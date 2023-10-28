from pymongo import MongoClient


class mongoClient:
    def __init__(self, db_server: str):
        self.client = MongoClient(db_server, serverSelectionTimeoutMS=5000)
        self.db = self.client["Boch"]
        self.collection_auth = self.db["auth"]
        self.collection_users = self.db["users"]
        self.collection_groups = self.db["groups"]
        self.collection_positions = self.db["positions"]
        self.collection_awsPolicies = self.db["awsPolicies"]
        self.collection_gcpRoles = self.db["gcpRoles"]

    def close_client(self):
        self.client.close()
