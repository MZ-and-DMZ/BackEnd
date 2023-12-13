import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from src.boto3_connect import aws_sdk
from src.database import mongodb
from src.utils import bson_to_json

from schemas import SwitchState

router = APIRouter(prefix="/logging/aws", tags=["logging aws"])


@router.get(path="/get/switch")
async def get_logging_switch():
    try:
        collection = mongodb.db["loggingSwitch"]
        query_result = await collection.find_one({"csp": "aws"})

        if query_result and "state" in query_result:
            duration = query_result["state"]
            res_json = bson_to_json({"state": duration})

            return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(path="/set/switch")
async def get_logging_switch(state: SwitchState):
    try:
        collection = mongodb.db["loggingSwitch"]
        query_result = await collection.update_one(
            {"csp": "aws"}, {"$set": {"state": state.state}}, upsert=True
        )

        if query_result.modified_count == 1 or query_result.upserted_id:
            return {"message": f"logging switch set to {state.state}"}
        else:
            return {"message": "failed to update switch state"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/set/duration")
async def set_aws_duration_value(duration: int):
    try:
        collection = mongodb.db["loggingDuration"]
        query_result = await collection.update_one(
            {"csp": "aws"}, {"$set": {"duration": duration}}, upsert=True
        )

        if query_result.modified_count == 1 or query_result.upserted_id:
            return {"message": f"duration set to {duration}"}
        else:
            return {"message": "duration not updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/get/duration")
async def get_aws_duration_value():
    try:
        collection = mongodb.db["loggingDuration"]
        query_result = await collection.find_one({"csp": "aws"})

        if query_result and "duration" in query_result:
            duration = query_result["duration"]
            res_json = bson_to_json({"duration": duration})

            return JSONResponse(content=res_json, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="duration not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/add/exception/user")
async def add_aws_user_exception(user_name: str):
    try:
        collection = mongodb.db["awsLoggingUserException"]
        current_time = datetime.now()
        query_result = await collection.insert_one(
            {"_id": user_name, "updateTime": current_time}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": f"{user_name} added successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to add")


@router.get(path="/list/exception/user")
async def get_aws_user_exception_list():
    try:
        collection = mongodb.db["awsLoggingUserException"]
        aws_users_collection = mongodb.db["awsUsers"]
        users_collection = mongodb.db["users"]
        query_result = await collection.find().to_list(length=None)

        for user in query_result:
            user["updateTime"] = user["updateTime"].strftime("%Y-%m-%d")

            aws_user = await aws_users_collection.find_one({"UserName": user["_id"]})
            if aws_user and "Groups" in aws_user and aws_user["Groups"]:
                user["groups"] = aws_user["Groups"]
            else:
                user["groups"] = None

            boch_user = await users_collection.find_one({"_id": user["_id"]})  # 이후에 awsAccount로 찾는 것으로 변경하기
            if (
                boch_user
                and "attachedPosition" in boch_user
                and boch_user["attachedPosition"]
            ):
                user["position"] = boch_user["attachedPosition"]
            else:
                user["position"] = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"user_exception_list": query_result})

    return JSONResponse(content=res_json, status_code=200)


@router.delete(path="/delete/exception/user")
async def delete_aws_user_exception(user_name: str):
    try:
        collection = mongodb.db["awsLoggingUserException"]
        query_result = await collection.delete_one({"_id": user_name})
        if query_result.deleted_count == 1:
            return {"message": "user delete success"}
        else:
            raise HTTPException(status_code=500, detail="deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
