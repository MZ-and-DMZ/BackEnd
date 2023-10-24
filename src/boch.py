import json

from bson import json_util
from bson.objectid import ObjectId
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


def get_boch_user(collection, user_id):
    try:
        query_result = collection.find_one({"_id": ObjectId(user_id)})
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


def update_boch_user(collection, user_id, user_data):
    try:
        query_result = collection.update_one(
            {"_id": user_id}, {"$set": user_data.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        return {"message": "user update success"}


def delete_boch_user(collection, user_id_list):
    delete_result = dict()  # 삭제 결과 JSON
    for user_id in user_id_list:
        try:
            query_result = collection.delete_one({"_id": user_id})  # 삭제
            if query_result.deleted_count == 1:
                delete_result[user_id] = "deleted successfully"
            else:
                delete_result[user_id] = "deletion failed"
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return delete_result


def get_boch_position_list(collection):
    try:
        query_result = list(collection.find())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"position_list": query_result})

    return JSONResponse(content=res_json, status_code=200)


def get_boch_position(collection, position_name):
    try:
        query_result = collection.find_one({"positionName": position_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result is None:
        raise HTTPException(status_code=404, detail="position not found")

    res_json = bson_to_json(query_result)

    return JSONResponse(content=res_json, status_code=200)


# 직무 생성하기
def create_position(position_data, collection):
    try:
        query_result = collection.insert_one(position_data.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": f"{position_data.positionName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create position")


# 직무 수정하기
def update_position(position_name, position_data, collection):
    try:
        query_result = collection.update_one(
            {"positionName": position_name}, {"$set": position_data.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="position not found")
    else:
        return {"message": "position update success"}


# 직무 삭제하기
def delete_position(collection, position_name_list):
    delete_result = dict()
    for position_name in position_name_list:
        try:
            position = collection.find_one({"positionName": position_name})

            if position is None:
                delete_result[position_name] = "position not found"
                continue
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # 직무 타입이 pre-define일 경우
        if position["isCustom"] is False:
            delete_result[position_name] = "cannot delete pre-defined position"
        else:
            query_result = collection.delete_one({"positionName": position_name})
            if query_result.deleted_count == 1:
                delete_result[position_name] = "deleted successfully"
            else:
                delete_result[position_name] = "deletion failed"

    return delete_result
