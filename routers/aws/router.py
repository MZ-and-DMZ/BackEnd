from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.boto3_connect import aws_sdk
from src.database import mongodb
from src.utils import bson_to_json

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
