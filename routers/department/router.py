from datetime import datetime
from typing import List

from fastapi import APIRouter, Body, HTTPException, Path
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get(path="/list")
async def list_department():
    collection = mongodb.db["depRole"]

    try:
        department_list = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for department in department_list:
        department.pop('_id', None)

    res_json = {"department_list": bson_to_json(department_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/userlist/{department_name}")
async def list_department_user(department_name: str = Path(..., title="department name")):
    collection = mongodb.db["depRole"]
    dep_exists = await collection.find_one({"department": department_name})
    if not dep_exists:
        raise HTTPException(status_code=404, detail=f"Department '{department_name}' not found")

    users_collection = mongodb.db["users"]
    aws_users_collection = mongodb.db["awsUsers"]

    try:
        user_list = await users_collection.find({"department": department_name}).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for user in user_list:
        aws_data = await aws_users_collection.find_one({"UserName": user["awsAccount"]})
        user["awsAccount"] = aws_data
        user["userName"] = user.pop("_id")

    res_json = {"user_list": bson_to_json(user_list)}

    return JSONResponse(content=res_json, status_code=200)