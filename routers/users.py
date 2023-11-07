from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from models import mongodb
from models.schemas import user
from src.util import bson_to_json

router = APIRouter(prefix="/users", tags=["users"])


@router.get(path="/all")
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
async def boch_create_user(user_data: user):
    collection = mongodb.db["users"]
    insert_data = user_data.dict()
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
