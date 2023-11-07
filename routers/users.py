from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from models import mongodb
from models.schemas import updateUser, user
from src.util import bson_to_json

router = APIRouter(prefix="/users", tags=["users"])


@router.get(path="/list")
async def get_user_list():
    collection = mongodb.db["users"]

    try:
        user_list = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"user_list": bson_to_json(user_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/{user_name}")
async def get_user(user_name: str = Path(..., title="user name")):
    collection = mongodb.db["users"]

    try:
        result = await collection.find_one({"userName": user_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result is None:
        raise HTTPException(status_code=404, detail="user not found")

    res_json = bson_to_json(result)

    return JSONResponse(content=res_json, status_code=200)


@router.post(path="/create")
async def create_user(user_data: user):
    collection = mongodb.db["users"]
    insert_data = user_data.dict()
    insert_data["_id"] = insert_data.pop("userName")
    insert_data["updatetime"] = datetime.now()
    try:
        insert_result = await collection.insert_one(insert_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if insert_result.acknowledged:
        # if user_data.attachedPosition is None:
        #     pass
        # else:
        #     aws_iam_sync.user_create_sync(user_data)

        return JSONResponse(
            content={"message": f"{user_data.userName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create user")


@router.put(path="/update/{user_name}")
async def update_user(
    user_data: updateUser, user_name: str = Path(..., title="user name")
):
    collection = mongodb.db["users"]
    new_user_data = user_data.dict()
    new_user_data["updatetime"] = datetime.now()

    try:
        old_user_data = await collection.find_one({"_id": user_name})
        update_result = await collection.update_one(
            {"_id": user_name}, {"$set": new_user_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        # 여기에 함수 삽입
        # aws_iam_sync.user_update_sync(origin_user_data, new_user_data)
        return {"message": "user update success"}


@router.delete(path="/delete/{user_name}")
async def delete_user(user_name: str = Path(..., title="user name")):
    collection = mongodb.db["users"]
    try:
        delete_result = collection.delete_one({"_id": user_name})  # 삭제
        if delete_result.deleted_count == 1:
            return {"message": "user delete success"}
        else:
            raise HTTPException(status_code=500, detail="deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))