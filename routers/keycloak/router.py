import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json

router = APIRouter(prefix="/idp", tags=["Keycloak"])

@router.get(path="/keycloak/groups")
async def get_keycloak_groups():
    try:
        collection = mongodb.db["keycloakGroups"]
        query_result = await collection.find({}).to_list(None)

        for group in query_result:
            group.pop("_id")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"groups": bson_to_json(query_result)}

    return JSONResponse(content=res_json, status_code=200)

@router.get(path="/keycloak/users")
async def get_keycloak_users() :
    try :
        collection = mongodb.db["keycloakUsers"]
        query_result = await collection.find({}).to_list(None)

        for user in query_result :
            user.pop("_id")
    except Exception as e :
        raise HTTPException(status_code=500, detail=str(e))
    res_json = {"users" : bson_to_json(query_result)}
    
    return JSONResponse(content=res_json, status_code=200)

@router.get(path="keycloak/clients")
async def get_keycloak_clients() :
    try : 
        collection = mongodb.db["keycloakClientsSummary"]
        query_result = await collection.find({}).to_list(None)

        for client in query_result :
            client.pop("_id")
    except Exception as e :
        raise HTTPException(status_code=500, detail=str(e))
    res_json = {"clients" : bson_to_json(query_result)}

    return JSONResponse(content=res_json, status_code=200)

@router.get(path="keycloak/roles")
async def get_keycloak_roles() :
    try : 
        collection = mongodb.db["keycloakRoles"]
        query_result = await collection.find({}).to_list(None)

        for role in query_result :
            role.pop("_id")
    except Exception as e :
        raise HTTPException(status_code=500, detail=str(e))
    res_json = {"roles" : bson_to_json(query_result)}

    return JSONResponse(content=res_json, status_code=200)