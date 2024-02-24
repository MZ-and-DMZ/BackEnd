from datetime import datetime
from typing import List

from fastapi import APIRouter, Body, HTTPException, Path
from fastapi.responses import JSONResponse

from src.aws_policy_control import attach_policy, detach_policy
from src.database import mongodb
from src.mfa_request import send_slack_message
from src.utils import bson_to_json

from .schemas import *

router = APIRouter(prefix="/users", tags=["users"])


@router.get(path="/list")
async def list_user():
    collection = mongodb.db["users"]
    aws_users_collection = mongodb.db["awsUsers"]
    aws_kms_collection = mongodb.db["awsKms"]
    try:
        user_list = await collection.find({"isRetire": False}).to_list(None)

        for user in user_list:
            aws_data = await aws_users_collection.find_one(
                {"UserName": user["awsAccount"]}
            )
            for key in aws_data["managedKeys"]:
                key_data = await aws_kms_collection.find_one({"_id": key})
                key_data["keyId"] = key_data.pop("_id")
                key_data.pop("adminstrators")
                key_data.pop("users")
                key = key_data
            for key in aws_data["usedKeys"]:
                key_data = await aws_kms_collection.find_one({"_id": key})
                key_data["keyId"] = key_data.pop("_id")
                key_data.pop("adminstrators")
                key_data.pop("users")
                key = key_data
            user["awsAccount"] = aws_data
            user["userName"] = user.pop("_id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"user_list": bson_to_json(user_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/{user_name}")
async def get_user(user_name: str = Path(..., title="user name")):
    collection = mongodb.db["users"]

    try:
        result = await collection.find_one({"_id": user_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result is None:
        raise HTTPException(status_code=404, detail="user not found")

    result["userName"] = result.pop("_id")
    aws_users = mongodb.db["awsUsers"]
    aws_user_find_result = await aws_users.find_one({"UserName": result["awsAccount"]})

    result["awsAccount"] = {
        "id": aws_user_find_result["UserName"],
        "lastLoginTime": aws_user_find_result.get("PasswordLastUsed"),
        "isMfaEnabled": aws_user_find_result.get("isMfaEnabled"),
        "managedKeys": [
            {
                "keyId": "6e67b820-d00e-4607-a16c-b340cfe23c76",
                "createDate": {"$date": "2024-01-02T11:25:36.570Z"},
                "keyExpirationDate": {"$date": "2024-02-01T11:25:36.570Z"},
            },
            {
                "keyId": "6e67b820-d00e-4607-a16c-b340cfe23c76",
                "createDate": {"$date": "2024-01-02T11:25:36.570Z"},
                "keyExpirationDate": {"$date": "2024-02-01T11:25:36.570Z"},
            },
        ],
        "usedKeys": [
            {
                "keyId": "6e67b820-d00e-4607-a16c-b340cfe23c76",
                "createDate": {"$date": "2024-01-02T11:25:36.570Z"},
                "keyExpirationDate": {"$date": "2024-02-01T11:25:36.570Z"},
            },
            {
                "keyId": "6e67b820-d00e-4607-a16c-b340cfe23c76",
                "createDate": {"$date": "2024-01-02T11:25:36.570Z"},
                "keyExpirationDate": {"$date": "2024-02-01T11:25:36.570Z"},
            },
        ],
    }

    res_json = bson_to_json(result)

    return JSONResponse(content=res_json, status_code=200)


@router.post(path="/create")
async def create_user(user_data: user):
    collection = mongodb.db["users"]
    insert_data = user_data.dict()
    insert_data["_id"] = insert_data.pop("userName")
    insert_data["updatetime"] = datetime.now()
    insert_data["isMfaEnabled"] = False
    insert_data["isRetire"] = False
    insert_data["lastLoginTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_data["isImportantPerson"] = False
    try:
        insert_result = await collection.insert_one(insert_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if insert_result.acknowledged:
        if user_data.attachedPosition is None:
            pass
        else:
            for position in user_data.attachedPosition:
                await attach_policy(
                    user_name=user_data.userName, position_name=position
                )

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
        old_position_list = old_user_data["attachedPosition"]
        new_position_list = new_user_data["attachedPosition"]
        attachment_position = list(set(new_position_list) - set(old_position_list))
        detachment_position = list(set(old_position_list) - set(new_position_list))
        for position in detachment_position:
            await detach_policy(user_name=user_name, position_name=position)
        for position in attachment_position:
            await attach_policy(user_name=user_name, position_name=position)
        return {"message": "user update success"}


@router.patch(path="/position/{user_name}")
async def attach_position(
    new_position_list: List[str] = Body(..., title="new position list"),
    user_name: str = Path(..., title="user name"),
):
    collection = mongodb.db["users"]
    find_result = await collection.find_one(
        {"_id": user_name}, {"_id": 0, "attachedPosition": 1}
    )
    old_position_list = find_result["attachedPosition"]

    update_result = await collection.update_one(
        {"_id": user_name}, {"$set": {"attachedPosition": new_position_list}}
    )
    attachment_position = set(new_position_list) - set(old_position_list)
    detachment_position = set(old_position_list) - set(new_position_list)
    # func(att)


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


@router.patch(path="/retire/{user_name}")
async def retire_user(user_name: str = Path(..., title="user name")):
    collection = mongodb.db["users"]
    try:
        update_result = await collection.update_one(
            {"_id": user_name}, {"$set": {"isRetire": True}}
        )
        # JIRA 알림 보내기
        return {"message": "user retire success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/request-mfa/{user_name}")
async def request_mfa_user(user_name: str = Path(..., title="user name")):
    try:
        title = f"To. {user_name}님"
        message = "AWS MFA가 설정되지 않았습니다. AWS MFA를 설정하세요."
        await send_slack_message(title, message)
        return {"message": "mfa request success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
