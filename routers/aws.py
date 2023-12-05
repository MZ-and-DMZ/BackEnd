import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models import mongodb
from src.boto3_connect import aws_sdk
from src.get_unused_user import is_unused
from src.util import bson_to_json

router = APIRouter(prefix="/aws", tags=["aws"])


@router.get(path="/policy/list")
async def list_aws_policy():
    collection = mongodb.db["awsPolicies"]
    try:
        policy_list = await collection.find(
            {}, {"_id": 1, "PolicyName": 1, "Description": 1, "CreateDate": 1}
        ).to_list(None)
        for policy in policy_list:
            policy["Arn"] = policy.pop("_id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"aws_policy_list": bson_to_json(policy_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/actioncrud")
async def get_action_crud():
    collection = mongodb.db["awsActionCRUD"]
    try:
        result = await collection.find().sort([("_id", 1)]).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"aws_action_crud": bson_to_json(result)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/servicelist")
async def get_service_list():
    aws_sdk.session_connect()
    services = aws_sdk.session.get_available_services()

    return services


@router.get(path="/unused-account")
async def get_unused_account():
    collection = mongodb.db["awsUsers"]
    aws_sdk.trail_connect()
    client = aws_sdk.client
    user_list = await collection.find({}, {"_id": 0, "UserName": 1}).to_list(None)
    tasks = [
        asyncio.create_task(is_unused(client, list(user_name.values())[0]))
        for user_name in user_list
    ]
    results = await asyncio.gather(*tasks)
    return [item for item in results if item is not None]
