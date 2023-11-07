from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models import mongodb
from src.util import bson_to_json

router = APIRouter(prefix="/aws", tags=["aws"])


@router.get(path="/policy/list")
async def get_aws_policy_list():
    collection = mongodb.db["awsPolicies"]
    try:
        policy_list = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"aws_policy_list": bson_to_json(policy_list)}

    return JSONResponse(content=res_json, status_code=200)
