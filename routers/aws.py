from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models import mongodb
from src.util import bson_to_json

router = APIRouter(prefix="/aws", tags=["aws"])


@router.get(path="/policy/list")
async def list_aws_policy():
    collection = mongodb.db["awsPolicies"]
    try:
        policy_list = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"aws_policy_list": bson_to_json(policy_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/actioncrud")
async def get_action_crud():
    collection = mongodb.db["awsActionCRUD"]
    try:
        result = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"aws_action_crud": bson_to_json(result)}

    return JSONResponse(content=res_json, status_code=200)
