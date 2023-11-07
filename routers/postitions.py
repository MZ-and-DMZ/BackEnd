from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from models import mongodb
from models.schemas import position, updatePosition
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


@router.post(path="/create")
async def create_position(position_data: position):
    collection = mongodb.db["positions"]
    insert_data = position_data.dict()
    insert_data["_id"] = insert_data.pop("positionName")

    try:
        insert_result = await collection.insert_one(insert_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if insert_result.acknowledged:
        return JSONResponse(
            content={"message": f"{position_data.positionName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create position")


@router.put(path="/update/{position_name}")
async def update_position(
    position_data: updatePosition, position_name: str = Path(..., title="position name")
):
    collection = mongodb.db["positions"]
    new_position_data = position_data.dict()

    try:
        update_result = await collection.update_one(
            {"_id": position_name}, {"$set": new_position_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="position not found")
    else:
        return {"message": "position update success"}


@router.delete(path="/delete/{position_name}")
async def delete_positions(position_name: str = Path(..., title="position name")):
    collection = mongodb.db["positions"]

    try:
        delete_result = await collection.delete_one({"_id": position_name})  # 삭제
        if delete_result.deleted_count == 1:
            return {"message": "position delete success"}
        else:
            raise HTTPException(status_code=500, detail="deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
