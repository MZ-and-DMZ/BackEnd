from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json

router = APIRouter(prefix="/compliance/ad", tags=["compliance ad"])


@router.get(path="/check/list")
async def aws_check_list():
    collection = mongodb.db["adCompliance"]
    try:
        check_list = await collection.find({}).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"ad_compliance_list": bson_to_json(check_list)}

    return JSONResponse(content=res_json, status_code=200)