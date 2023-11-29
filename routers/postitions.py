from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from models import mongodb
from models.schemas import position, updatePosition
from src.create_position import create_position_aws
from src.util import bson_to_json

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get(path="/list")
async def list_position():
    collection = mongodb.db["positions"]

    try:
        position_list = await collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    awsPolicies = mongodb.db["awsPolicies"]
    gcpRoles = mongodb.db["gcpRoles"]
    for position in position_list:
        position["positionName"] = position.pop("_id")
        if position["csp"] == "aws":
            for policy in position["policies"]:
                value = list(policy.values())[0]
                policy_data = await awsPolicies.find_one({"_id": value})
                policy["description"] = policy_data.get("Description")
        elif position["csp"] == "gcp":
            for policy in position["policies"]:
                value = list(policy.values())[0]
                policy_data = await gcpRoles.find_one({"name": value})
                policy["description"] = policy_data.get("Description")

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
    insert_data = position_data.dict()
    insert_data["_id"] = insert_data.pop("positionName")

    if position_data.csp == "aws":
        policies = insert_data.pop("policies")
        insert_data["policies"] = []
        collection = mongodb.db["awsPolicies"]
        for policy in policies:
            policy_data = await collection.find_one({"PolicyName": policy})
            data = {policy: policy_data["_id"]}
            insert_data["policies"].append(data)
        await create_position_aws(
            position_name=insert_data["_id"],
            policies=insert_data["policies"],
        )
    elif position_data.csp == "gcp":
        policies = insert_data.pop("policies")
        insert_data["policise"] = []
        collection = mongodb.db["gcpRoles"]
        for policy in policies:
            policy_data = await collection.find_one({"title": policy})
            data = {policy: policy_data["_id"]}
            insert_data["policise"].append(data)
    try:
        collection = mongodb.db["positions"]
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


@router.get(path="/convert/{position_name}")
async def convert_positions(position_name: str = Path(..., title="position name")):
    collection = mongodb.db["positions"]

    try:
        position_data = await collection.find_one({"_id": position_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if position_data is None:
        raise HTTPException(status_code=404, detail="position not found")

    collection = mongodb.db["awsPolicyRefer"]
    policies = position_data["policies"]
    convert_policies = []
    for policy in policies:
        arn = list(policy.values())
        cursor = await collection.find_one({"_id": arn[0]})
        if cursor is None:
            continue
        else:
            role_list = list(cursor["gcp"][0].values())
            convert_policies.extend(role_list)

    res_json = {"convert_policies": list(set(convert_policies))}

    return JSONResponse(content=res_json, status_code=200)
