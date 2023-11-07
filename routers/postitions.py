from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from models import mongodb
from models.schemas import updateUser, user
from src.util import bson_to_json

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get(path="/list")
async def get_position_list():
    collection = mongodb.db["positions"]

    try:
        position_list = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for position in position_list:
        position["positionName"] = position.pop("_id")

    res_json = {"position_list": bson_to_json(position_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/{position_name}")
async def get_position(position_name: str = Path(..., title="position name")):
    collection = mongodb.db["positions"]

    try:
        result = await collection.find_one({"_id": position_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result is None:
        raise HTTPException(status_code=404, detail="position not found")

    res_json = bson_to_json(result)

    return JSONResponse(content=res_json, status_code=200)
