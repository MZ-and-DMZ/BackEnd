import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json

from .schemas import SwitchState

router = APIRouter(prefix="/logging/gcp", tags=["logging gcp"])


@router.get(path="/get/switch")
async def get_logging_switch():
    try:
        collection = mongodb.db["loggingSwitch"]
        query_result = await collection.find_one({"csp": "gcp"})

        if query_result and "state" in query_result:
            state = query_result["state"]
            res_json = bson_to_json({"state": state})

            return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(path="/set/switch")
async def get_logging_switch(state: SwitchState):
    try:
        collection = mongodb.db["loggingSwitch"]
        query_result = await collection.update_one(
            {"csp": "gcp"}, {"$set": {"state": state.state}}, upsert=True
        )

        if query_result.modified_count == 1 or query_result.upserted_id:
            return {"message": f"logging switch set to {state.state}"}
        else:
            return {"message": "failed to update switch state"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/set/duration")
async def set_gcp_duration_value(duration: int):
    try:
        collection = mongodb.db["loggingDuration"]
        query_result = await collection.update_one(
            {"csp": "gcp"}, {"$set": {"duration": duration}}, upsert=True
        )

        if query_result.modified_count == 1 or query_result.upserted_id:
            return {"message": f"duration set to {duration}"}
        else:
            return {"message": "duration not updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/get/duration")
async def get_gcp_duration_value():
    try:
        collection = mongodb.db["loggingDuration"]
        query_result = await collection.find_one({"csp": "gcp"})

        if query_result and "duration" in query_result:
            duration = query_result["duration"]
            res_json = bson_to_json({"duration": duration})

            return JSONResponse(content=res_json, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="duration not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/add/exception/member")
async def add_gcp_member_exception(member_name: str, type: str):
    try:
        collection = mongodb.db["gcpLoggingMemberException"]
        current_time = datetime.now()
        query_result = await collection.insert_one(
            {"_id": member_name, "type": type, "updateTime": current_time}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": f"{member_name} added successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to add")


@router.get(path="/list/exception/member")
async def get_gcp_member_exception_list():
    try:
        collection = mongodb.db["gcpLoggingMemberException"]
        users_collection = mongodb.db["users"]
        groups_collection = mongodb.db["groups"]
        query_result = await collection.find().to_list(length=None)

        for member in query_result:
            member["updateTime"] = member["updateTime"].strftime("%Y-%m-%d")

            if member["type"] == "user":
                boch_user = await users_collection.find_one({"_id": member["_id"]})  # 이후에 gcpAccount로 찾는 것으로 변경하기
                if (
                    boch_user
                    and "attachedPosition" in boch_user
                    and boch_user["attachedPosition"]
                ):
                    member["position"] = boch_user["attachedPosition"]
                else:
                    member["position"] = None
            elif member["type"] == "group":
                boch_group = await groups_collection.find_one({"groupName": member["_id"]})  # 이후에 gcpGroup으로 찾는 것으로 변경하기
                if (
                    boch_group
                    and "attachedPosition" in boch_group
                    and boch_group["attachedPosition"]
                ):
                    member["position"] = boch_group["attachedPosition"]
                else:
                    member["position"] = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"member_exception_list": query_result})

    return JSONResponse(content=res_json, status_code=200)


@router.delete(path="/delete/exception/member")
async def delete_gcp_member_exception(member_name: str):
    try:
        collection = mongodb.db["gcpLoggingMemberException"]
        query_result = await collection.delete_one({"_id": member_name})
        if query_result.deleted_count == 1:
            return {"message": "member delete success"}
        else:
            raise HTTPException(status_code=500, detail="deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
