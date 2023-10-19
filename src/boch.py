import json

from bson import json_util
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from database import db_client
from bson.objectid import ObjectId


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


# 테스트용, 작동은 하는데 이 형태가 효율적인지에 대해서는 고민 필요 (정리 안했음)
# 직무 생성 시 빈칸인지 확인, iscustom이 true인지 확인 등이 필요 > 프론트?
def update_position2(position_id, position_data, collection, user_update, user_collection):
    try:
        position = collection.find_one({"_id": ObjectId(position_id)})

        if position is None:
            raise HTTPException(status_code=404, detail="position not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if position["isCustom"] is True:
        query_result = collection.update_one(
            {"_id": ObjectId(position_id)}, {"$set": position_data.dict()}
        )

        if query_result.modified_count > 0:
            return {"message": "position update success"}
        else:
            raise HTTPException(status_code=404, detail="position not updated")
    else:
        new_position_data = {
            "isCustom": True,
            **position_data.dict(),
        }
        query_result = collection.insert_one(new_position_data)
        new_position_id = query_result.inserted_id  # ObjectID로 저장 시
        # new_position_id = str(query_result.inserted_id) - 문자열로 저장 시

        if user_update:
            user_collection.update_many(
                {"attachedPosition": ObjectId(position_id)},
                # {"attachedPosition": position_id},
                {"$set": {"attachedPosition.$": new_position_id}},
            )

        return {"message": f"Position updated with new ID: {new_position_id}"}