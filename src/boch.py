import json

from bson import json_util
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def bson_to_json(data):
    return json.loads(json_util.dumps(data))


def get_boch_user_list(collection):
    try:
        query_result = list(collection.find())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"user_list": query_result})

    return JSONResponse(content=res_json, status_code=200)


def get_boch_user(collection, user_name):
    try:
        query_result = collection.find_one({"userName": user_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result is None:
        raise HTTPException(status_code=404, detail="user not found")

    res_json = bson_to_json(query_result)
    return JSONResponse(content=res_json, status_code=200)


def create_boch_user(collection, user_data):
    try:
        query_result = collection.insert_one(user_data.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": f"{user_data.userName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create user")


def update_boch_user(collection, user_name, user_data):
    try:
        query_result = collection.update_one(
            {"userName": user_name}, {"$set": user_data.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        return {"message": "user update success"}


def delete_boch_user(collection, user_name_list):
    delete_result = dict()  # 삭제 결과 JSON
    for user_name in user_name_list:
        try:
            query_result = collection.delete_one({"userName": user_name})  # 삭제
            if query_result.deleted_count == 1:
                delete_result[user_name] = "deleted successfully"
            else:
                delete_result[user_name] = "deletion failed"
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return delete_result


def get_boch_position_list(collection):
    try:
        query_result = list(collection.find())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"position_list": bson_to_json(query_result)}


def get_boch_position(collection, position_name):
    try:
        query_result = collection.find_one({"positionName": position_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result is None:
        raise HTTPException(status_code=404, detail="user not found")

    res_json = bson_to_json(query_result)
    return JSONResponse(content=res_json, status_code=200)


# 직무 생성하기
def create_position(position_data, collection):
    try:
        query_result = collection.insert_one(position_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": f"{position_data.userName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create position")


# 직무 수정하기
def update_position(position_id, position, collection):
    existing_position = collection.find_one({"_id": position_id})

    if existing_position is None:
        return {"result": "position not found"}

    update_query = {
        "$set": {
            "_id": position.position_name,
            "type": position.type,
            "description": position.description,
            "aws_policies": position.aws_policies,
            "gcp_policies": position.gcp_policies,
        }
    }

    try:
        result = collection.update_one({"_id": position_id}, update_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result.modified_count > 0:
        return {"result": f"{position_id} updated successfully"}
    else:
        return {"result": f"no modifications for {position_id}"}


# 직무 삭제하기
def delete_position(collection, position_id_list):
    result = dict()
    for position_id in position_id_list:
        try:
            position = collection.find_one({"_id": position_id})

            if position is None:
                result[position_id] = "position not found"
                continue
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # 직무 타입이 pre-define일 경우
        if position["type"] == "pre_define":
            result[position_id] = "cannot delete pre-defined position"
        else:
            delete_result = collection.delete_one({"_id": position_id})
            if delete_result.deleted_count == 1:
                result[position_id] = "deleted successfully"
            else:
                result[position_id] = "deletion failed"

    return result
