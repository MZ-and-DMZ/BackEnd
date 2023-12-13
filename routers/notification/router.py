from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json

from .schemas import *

router = APIRouter(prefix="/notification", tags=["notification"])


@router.get(path="/list")
async def list_notification():
    collection = mongodb.db["notification"]
    try:
        notification_list = await collection.find(
            {"isShow": True}, {"detail": 0, "isShow": 0}
        ).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for notification in notification_list:
        notification["_id"] = str(notification["_id"])
    res_json = {"notification_list": bson_to_json(notification_list)}
    collection.update_many(
        {"isRead": False}, {"$set": {"isRead": True}}
    )  # api 호출 시 읽었다고 간주
    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/all")
async def list_notification():
    collection = mongodb.db["notification"]
    try:
        notification_list = await collection.find(
            {}, {"detail": 0, "isShow": 0}
        ).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for notification in notification_list:
        notification["_id"] = str(notification["_id"])
    res_json = {"notification_list": bson_to_json(notification_list)}
    collection.update_many(
        {"isRead": False}, {"$set": {"isRead": True}}
    )  # api 호출 시 읽었다고 간주
    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/check-new")
async def check_new_notification():
    collection = mongodb.db["notification"]
    try:
        is_new = await collection.find({"isRead": False}).to_list(1)
        if is_new:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/create")
async def create_notification(data: notification):
    collection = mongodb.db["notification"]
    insert_data = data.dict()
    insert_data["createtime"] = datetime.now()
    insert_data["isRead"] = False
    insert_data["isShow"] = True
    try:
        insert_result = await collection.insert_one(insert_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
