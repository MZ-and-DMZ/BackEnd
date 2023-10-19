from typing import List

from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from database import db_client
from model import model
from src import boch, login
from src.config import conf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


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
    return FileResponse("./public/index.html")


@app.post(path="/login")
def auth(user: model.auth):
    global client
    return login.auth_user(user, client.collection_auth)


@app.get(path="/boch/get/userlist")
def boch_get_user_list():
    return boch.get_boch_user_list(client.collection_users)


@app.get(path="/boch/get/user/{user_name}")
def boch_get_user(user_name: str = Path(..., title="user name")):
    return boch.get_boch_user(client.collection_users, user_name)


@app.post(path="/boch/create/user")
def boch_create_user(user_data: model.user):
    return boch.create_boch_user(client.collection_users, user_data)


@app.put(path="/boch/update/user/{user_name}")
def boch_update_user(
    user_data: model.user, user_name: str = Path(..., title="user name")
):
    return boch.update_boch_user(client.collection_users, user_name, user_data)


@app.delete(path="/boch/delete/user")
def boch_delete_user(user_name_list: List[str]):
    return boch.delete_boch_user(client.collection_users, user_name_list)


@app.get(path="/boch/get/positionlist")
def boch_get_position_list():
    return boch.get_boch_position_list(client.collection_positions)


@app.get(path="/boch/get/position/{position_name}")
def boch_get_position(position_name: str = Path(..., title="position name")):
    return boch.get_boch_position(client.collection_positions, position_name)


@app.post(path="/boch/create/position")
def create_position(position: model.position):
    return boch.create_position(position, client.collection_positions)


@app.put(path="/boch/update/position/{position_name}")
def update_position(
    position: model.position, position_name: str = Path(..., title="position name")
):
    return boch.update_position(position_name, position, client.collection_positions)


@app.delete(path="/boch/delete/position")
def delete_positions(position_name_list: List[str]):
    return boch.delete_position(client.collection_positions, position_name_list)


@app.put(path="/boch/update/position/test/{position_id}")
def update_position2(
    position: model.position, user_update: bool, position_id: str = Path(..., title="position id")
):
    return boch.update_position2(position_id, position, client.collection_positions, user_update, client.collection_users)