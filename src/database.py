from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    def __init__(self):
        self.client = None

    def connect(self, db_server_url):
        self.client = AsyncIOMotorClient(db_server_url)
        self.db_Boch = self.client["Boch"]

    def close(self):
        self.client.close()


mongodb = MongoDB()
