from typing import List

from fastapi import FastAPI, Path

from database import db_client
from model import model
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


@app.post(path="/login")
def auth(user: model.Auth):
    global client
    return login.auth_user(user, client.collection_auth)


@app.get(path="/boch/get/userlist")
def boch_get_user_list():
    return boch.get_boch_user_list(client.collection_users)


@app.get(path="/boch/get/user/{user_id}")
def boch_get_user(user_id: str = Path(..., title="user_id")):
    return boch.get_boch_user(client.collection_users, user_id)


@app.post(path="/boch/create/user")
def boch_create_user(user_data: model.Users):
    return boch.create_boch_user(client.collection_users, user_data)


@app.put(path="/boch/update/user")
def boch_update_user(user_data: model.Users):
    return boch.update_boch_user(client.collection_users, user_data)


@app.delete(path="/boch/delete/user")
def boch_delete_user(user_id_list: List[str]):
    return boch.delete_boch_user(client.collection_users, user_id_list)


@app.get(path="/boch/get/positionlist")
def boch_get_position_list():
    return boch.get_boch_position_list(client.collection_position)


@app.get(path="/boch/get/position/{position_id}")
def boch_get_position(position_id: str = Path(..., title="Position ID")):
    return boch.get_boch_position(client.collection_position, position_id)


@app.delete(path="/boch/delete/position")
def delete_positions(position_id_list: List[str]):
    return boch.delete_position(client.collection_position, position_id_list)


@app.post(path="/boch/create/position")
def create_position(position: model.Position):
    return boch.create_position(position, client.collection_position)
