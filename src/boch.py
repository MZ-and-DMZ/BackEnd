import json

from bson import json_util
from bson.objectid import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from .aws_sdk import awsSDK
from .csp_iam_sync import iamSync

aws_iam_sync = awsIamSync()
iam_sync = iamSync()
aws_sdk = awsSDK()


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
        if user_data.attachedPosition is None:
            pass
        else:
            aws_iam_sync.user_create_sync(user_data)

        return JSONResponse(
            content={"message": f"{user_data.userName} created successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to create user")


def update_boch_user(collection, user_id, new_user_data):
    try:
        origin_user_data = collection.find_one({"_id": ObjectId(user_id)})
        query_result = collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": new_user_data.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        # 여기에 함수 삽입
        aws_iam_sync.user_update_sync(origin_user_data, new_user_data)
        return {"message": "user update success"}


def update_boch_user_info(collection, user_id, new_user_data):
    pass


def update_boch_user_position(collection, user_id, new_user_data):
    pass


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


def create_boch_group(group_data, collection, user_collection):
    try:
        query_result = collection.insert_one(group_data.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        if group_data.awsGroup:  # awsGroup을 입력한 경우
            try:
                aws_sdk.create_group(group_data.awsGroup)  # aws 그룹 생성
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

            if group_data.users:  # users를 입력한 경우
                for user_id in group_data.users:
                    user_document = user_collection.find_one({"_id": ObjectId(user_id)})
                    if user_document:
                        aws_account = user_document.get("awsAccount")
                        if aws_account:
                            try:
                                aws_sdk.add_user_to_group(
                                    group_data.awsGroup, aws_account
                                )  # aws 그룹에 사용자 추가
                                user_collection.update_one(
                                    {"_id": ObjectId(user_id)},
                                    {
                                        "$set": {
                                            "attachedGroup.$": str(
                                                query_result.inserted_id
                                            )
                                        }
                                    },
                                )  # users 데이터에 attachedGroup 추가
                                aws_sdk.update_awsUsers(
                                    aws_account
                                )  # awsUsers 변경 사항 반영
                            except Exception as e:
                                raise HTTPException(status_code=500, detail=str(e))

            if group_data.attachedPosition:  # attachedPosition을 입력한 경우
                for position_id in group_data.attachedPosition:
                    try:
                        aws_sdk.attach_group_position(
                            group_data.awsGroup, position_id
                        )  # 직무 처리 및 aws 그룹에 정책으로 연결
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=str(e))

            aws_sdk.update_awsGroups(group_data.awsGroup)  # awsGroups 변경 사항 반영
        elif group_data.gcpGroup:  # gcpGroup을 입력한 경우
            pass

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
