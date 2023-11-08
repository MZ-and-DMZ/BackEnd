from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models import mongodb
from src.util import bson_to_json

router = APIRouter(prefix="/gcp", tags=["gcp"])


@router.get(path="/role/list")
async def list_gcp_role():
    collection = mongodb.db["gcpRoles"]
    try:
        role_list = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"gcp_role_list": bson_to_json(role_list)}

    return JSONResponse(content=res_json, status_code=200)
