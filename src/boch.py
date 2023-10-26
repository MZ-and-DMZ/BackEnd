import json

from bson import json_util
from bson.objectid import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from .csp_iam_sync import iamSync

iam_sync = iamSync()


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
        # 이 부분에 함수 삽입
        if user_data.attachedPosition is None:
            pass
        else:
            iam_sync.user_create_sync(user_data)

        return JSONResponse(
            content={"message": f"{user_data.userName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create user")


def update_boch_user(collection, user_id, user_data):
    try:
        query_result = collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": user_data.dict()}
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
            query_result = collection.delete_one({"_id": ObjectId(user_id)})  # 삭제
            if query_result.deleted_count == 1:
                delete_result[user_id] = "deleted successfully"
            else:
                delete_result[user_id] = "deletion failed"
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return delete_result


def get_boch_group_list(collection):
    try:
        query_result = list(collection.find())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"group_list": query_result})

    return JSONResponse(content=res_json, status_code=200)


def get_boch_group(collection, group_id):
    try:
        query_result = collection.find_one({"_id": ObjectId(group_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result is None:
        raise HTTPException(status_code=404, detail="group not found")

    res_json = bson_to_json(query_result)

    return JSONResponse(content=res_json, status_code=200)


# aws, gcp group 있는지 확인 -> 생성
def create_boch_group(group_data, collection):
    try:
        query_result = collection.insert_one(group_data.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        # 이 부분에 함수 삽입
        if group_data.attachedPosition is None:
            pass
        else:
            iam_sync.group_create_sync(group_data)
        
        if group_data.users is None:
            pass
        #user db에도 넣어야 함

        return JSONResponse(
            content={"message": f"{group_data.groupName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create group")


# 기존의 Name(group, users)과 수정한 Name이 다르면 user_collection에서 바꾸기 - ObjectID가 아닐 경우
def update_boch_group(group_id, group_data, collection, user_collection):
    try:
        query_result = collection.update_one(
            {"_id": ObjectId(group_id)}, {"$set": group_data.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="group not found")
    elif query_result.modified_count > 0:
        return {"message": "group update success"}
    else:
        raise HTTPException(status_code=404, detail="group not updated")


def delete_boch_group(collection, group_id_list):
    delete_result = dict()  # 삭제 결과 JSON
    for group_id in group_id_list:
        try:
            query_result = collection.delete_one({"_id": ObjectId(group_id)})  # 삭제
            if query_result.deleted_count == 1:
                delete_result[group_id] = "deleted successfully"
            else:
                delete_result[group_id] = "deletion failed"
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


def get_boch_position(collection, position_id):
    try:
        query_result = collection.find_one({"_id": ObjectId(position_id)})
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
def update_position(position_id, position_data, collection, user_collection):
    try:
        position = collection.find_one({"_id": ObjectId(position_id)})
        if not position:
            raise HTTPException(status_code=404, detail="position not found")

        if position["isCustom"]:  # 커스텀 직무라면 원본 데이터를 수정
            query_result = collection.update_one(
                {"_id": ObjectId(position_id)}, {"$set": position_data.dict()}
            )

            if query_result.modified_count > 0:
                return {"message": "position update successful"}
            else:
                raise HTTPException(status_code=404, detail="position not updated")
        else:  # 솔루션 제공 직무라면 복사본 생성 후 수정
            new_position_data = {
                "isCustom": True,
                **position_data.dict(),
            }
            query_result = collection.insert_one(new_position_data)
            user_collection.update_many(
                {"attachedPosition": ObjectId(position_id)},  # 문자열로 삽입 시 ObjectID() 삭제
                {
                    "$set": {"attachedPosition.$": query_result.inserted_id}
                },  # 문자열로 삽입 시 str() 추가
            )
            return {
                "message": f"position updated with new ID: {query_result.inserted_id}"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 직무 삭제하기
def delete_position(collection, position_id_list):
    delete_result = dict()
    for position_id in position_id_list:
        try:
            position = collection.find_one({"_id": ObjectId(position_id)})

            if position is None:
                delete_result[position_id] = "position not found"
                continue
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # 직무 타입이 pre-define일 경우
        if position["isCustom"] is False:
            delete_result[position_id] = "cannot delete pre-defined position"
        else:
            query_result = collection.delete_one({"_id": ObjectId(position_id)})
            if query_result.deleted_count == 1:
                delete_result[position_id] = "deleted successfully"
            else:
                delete_result[position_id] = "deletion failed"

    return delete_result


def get_aws_policy_list(collection):
    try:
        query_result = list(collection.find())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"aws_policy_list": query_result})

    return JSONResponse(content=res_json, status_code=200)


def get_gcp_role_list(collection):
    try:
        query_result = list(collection.find())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"gcp_role_list": query_result})

    return JSONResponse(content=res_json, status_code=200)
