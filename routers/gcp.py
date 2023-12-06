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


@router.get(path="/actioncrud")
async def get_action_crud():
    collection = mongodb.db["gcpActionCRUD"]
    try:
        result = await collection.find().sort([("_id", 1)]).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"gcp_action_crud": bson_to_json(result)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/servicelist")
async def get_service_list():
    collection = mongodb.db["gcpActionCRUD"]
    try:
        result = await collection.find({}, {"_id": 1}).sort([("_id", 1)]).to_list(None)
        service_list = []
        for service in result:
            service_list.append(service["_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = service_list

    return JSONResponse(content=res_json, status_code=200)
