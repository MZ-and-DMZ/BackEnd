import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json

router = APIRouter(prefix="/window_ad", tags=["WindowsActiveDirectory"])

@router.get(path="/groups")
async def get_ad_groups():
    try:
        collection = mongodb.db["windowsADGroup"]
        query_result = await collection.find({}).to_list(None)

        for group in query_result:
            group.pop("_id")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"groups": bson_to_json(query_result)}

    return JSONResponse(content=res_json, status_code=200)

@router.get(path="/users")
async def get_ad_users() :
    try :
        collection = mongodb.db["windowsADPerson"]
        query_result = await collection.find({}).to_list(None)

        for user in query_result :
            user.pop("_id")
    except Exception as e :
        raise HTTPException(status_code=500, detail=str(e))
    res_json = {"users" : bson_to_json(query_result)}
    
    return JSONResponse(content=res_json, status_code=200)
