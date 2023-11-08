from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from models import mongodb
from models.schemas import group, updateGroup
from src.util import bson_to_json

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get(path="/boch/get/grouplist")
async def get_group_list():
    collection = mongodb.db["groups"]

    try:
        group_list = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for group in group_list:
        group["groupName"] = group.pop("_id")

    res_json = {"group_list": bson_to_json(group_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/{group_name}")
async def get_group(group_name: str = Path(..., title="group name")):
    collection = mongodb.db["groups"]

    try:
        result = await collection.find_one({"_id": group_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result is None:
        raise HTTPException(status_code=404, detail="group not found")

    result["groupName"] = result.pop("_id")

    res_json = bson_to_json(result)

    return JSONResponse(content=res_json, status_code=200)


@router.post(path="/create")
async def create_group(group_data: group):
    collection = mongodb.db["groups"]
    insert_data = group_data.dict()
    insert_data["_id"] = insert_data.pop("groupName")
    insert_data["updatetime"] = datetime.now()
    try:
        insert_result = await collection.insert_one(insert_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if insert_result.acknowledged:
        return JSONResponse(
            content={"message": f"{group_data.groupName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create user")


@router.put(path="/update/{group_name}")
async def update_group(
    group_data: updateGroup, group_name: str = Path(..., title="group name")
):
    collection = mongodb.db["groups"]
    new_group_data = group_data.dict()
    new_group_data["updatetime"] = datetime.now()

    try:
        old_group_data = await collection.find_one({"_id": group_name})
        update_result = await collection.update_one(
            {"_id": group_name}, {"$set": new_group_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="group not found")
    else:
        return {"message": "group update success"}


@router.delete(path="/delete/{group_name}")
async def delete_group(group_name: str = Path(..., title="group name")):
    collection = mongodb.db["groups"]
    try:
        delete_result = collection.delete_one({"_id": group_name})  # 삭제
        if delete_result.deleted_count == 1:
            return {"message": "user delete success"}
        else:
            raise HTTPException(status_code=500, detail="deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
