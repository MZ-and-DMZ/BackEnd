from fastapi import FastAPI

from database import db_client
from model.user_auth import UserAuth
from src import boch, login
from src.config import conf

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    global client
    client = db_client.mongoClient(conf["DB_server"])


@app.on_event("shutdown")
async def shutdown_event():
    global client
    client.close_client()


@app.get(path="/")
async def root():
    return {"message": "Hello World!"}


# 로그인 API 엔드포인트 정의
@app.post(path="/login")
def auth(user: UserAuth):
    return login.auth_user(user, client.collection_auth)


@app.get(path="/boch/get/userlist")
def boch_get_user_list():
    return boch.get_boch_user_list(client.collection_users)


@app.get(path="/boch/get/positionlist")
def boch_get_position_list():
    return boch.get_boch_position_list(client.collection_position)
