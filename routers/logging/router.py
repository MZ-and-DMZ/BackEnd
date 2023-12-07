import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from src.boto3_connect import aws_sdk
from src.database import mongodb
from src.utils import bson_to_json

router = APIRouter(prefix="/logging", tags=["logging"])


@router.get(path="/list")
async def get_logging_list():
    collection = mongodb.db["awsMatchUserAction"]
    try:
        pipeline = [
            {"$sort": {"updateTime": -1}},
            {
                "$project": {
                    "user_name": 1,
                    "latest_history_date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": {"$arrayElemAt": ["$history.date", -1]},
                        }
                    },
                    "latest_history_version": {
                        "$arrayElemAt": ["$history.version", -1]
                    },
                }
            },
        ]

        logging_list = []
        async for document in collection.aggregate(pipeline):
            logging_list.append(document)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"logging_list": logging_list})

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/history/{user_name}")
async def get_logging_user_history(user_name: str = Path(..., title="user name")):
    try:
        collection = mongodb.db["awsMatchUserAction"]
        query_result = await collection.find_one({"user_name": user_name})
        result = []
        history = query_result.get("history", [])
        collection = mongodb.db["awsUserActions"]
        for i in range(1, min(6, len(history) + 1)):
            latest_history = history[-i]
            action_data = await collection.find_one({"_id": latest_history["action"]})
            action_list = action_data.get("action_list", [])
            action_count = len(action_list)
            result.append(
                {
                    "date": latest_history["date"].strftime("%Y-%m-%d"),
                    "version": latest_history["version"],
                    "action_id": latest_history["action"],
                    "action_list": action_list,
                    "action_count": action_count,
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"logging_user_history": result})

    return JSONResponse(content=res_json, status_code=200)


@router.post(path="/rollback/{user_name}")
async def logging_rollback(version: int, user_name: str = Path(..., title="user name")):
    try:
        aws_sdk.iam_connect()
        iam_client = aws_sdk.client
        match_collection = mongodb.db["awsMatchUserAction"]
        query_result = await match_collection.find_one({"user_name": user_name})

        # 사용자에게 연결된 정책 분리 및 삭제
        if "attachedCustomerPolicy" in query_result:
            current_policy_arn = query_result["attachedCustomerPolicy"]
            # 정책을 사용자에게서 분리
            iam_client.detach_user_policy(
                UserName=user_name, PolicyArn=current_policy_arn
            )
            # 정책 삭제
            iam_client.delete_policy(PolicyArn=current_policy_arn)

        selected_record = query_result["history"][version - 1]
        updated_version = query_result["history"][-1]["version"] + 1
        selected_date = selected_record["date"]
        selected_id = selected_record["action"]
        selected_arn = selected_record["arn"]

        # DB에 저장된 정책 문서 가져오기
        collection = mongodb.db["awsCustomerPolicy"]
        document_result = await collection.find_one({"_id": selected_arn})
        policy_document = document_result["document"]
        # 정책 이름 설정
        # ARN을 ':' 문자를 기준으로 분할하고 마지막 부분을 선택
        policy_name_split = selected_arn.split(":")[-1]
        # '/' 문자를 기준으로 분할하고 두 번째 부분을 선택
        policy_name = policy_name_split.split("/")[1]
        # 고객 관리형 정책 생성
        response = iam_client.create_policy(
            PolicyName=policy_name, PolicyDocument=json.dumps(policy_document)
        )
        policy_arn = response["Policy"]["Arn"]
        # print(f"Policy Created: {policy_arn}")
        # 사용자에게 정책 연결
        iam_client.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)

        await match_collection.update_one(
            {"user_name": user_name},
            {
                "$set": {
                    "attachedCustomerPolicy": selected_arn,
                    "updateTime": datetime.now(),
                    f"history.{updated_version - 1}.date": datetime.now(),
                    f"history.{updated_version - 1}.action": selected_id,
                    f"history.{updated_version - 1}.version": updated_version,
                    f"history.{updated_version - 1}.arn": selected_arn,
                }
            },
        )
        return {"message": "rollback success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/set/duration/aws")
async def set_aws_duration_value(duration: int):
    try:
        collection = mongodb.db["loggingDuration"]
        query_result = await collection.update_one(
            {"csp": "aws"}, {"$set": {"duration": duration}}, upsert=True
        )

        if query_result.modified_count == 1 or query_result.upserted_id:
            return {"message": f"duration set to {duration}"}
        else:
            return {"message": "duration not updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/set/duration/gcp")
async def set_gcp_duration_value(duration: int):
    try:
        collection = mongodb.db["loggingDuration"]
        query_result = await collection.update_one(
            {"csp": "gcp"}, {"$set": {"duration": duration}}, upsert=True
        )

        if query_result.modified_count == 1 or query_result.upserted_id:
            return {"message": f"duration set to {duration}"}
        else:
            return {"message": "duration not updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/get/duration/aws")
async def get_aws_duration_value():
    try:
        collection = mongodb.db["loggingDuration"]
        query_result = await collection.find_one({"csp": "aws"})

        if query_result and "duration" in query_result:
            duration = query_result["duration"]
            res_json = bson_to_json({"duration": duration})

            return JSONResponse(content=res_json, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="duration not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/get/duration/gcp")
async def get_gcp_duration_value():
    try:
        collection = mongodb.db["loggingDuration"]
        query_result = await collection.find_one({"csp": "gcp"})

        if query_result and "duration" in query_result:
            duration = query_result["duration"]
            res_json = bson_to_json({"duration": duration})

            return JSONResponse(content=res_json, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="duration not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/add/exception/user/aws")
async def add_aws_user_exception(user_name: str):
    try:
        collection = mongodb.db["awsLoggingUserException"]
        current_time = datetime.now()
        query_result = await collection.insert_one(
            {"_id": user_name, "updateTime": current_time}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": f"{user_name} added successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to add")


@router.post(path="/add/exception/member/gcp")
async def add_gcp_member_exception(member_name: str, type: str):
    try:
        collection = mongodb.db["gcpLoggingMemberException"]
        current_time = datetime.now()
        query_result = await collection.insert_one(
            {"_id": member_name, "type": type, "updateTime": current_time}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": f"{member_name} added successfully"},
            status_code=201,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to add")


@router.get(path="/list/exception/user/aws")
async def get_aws_user_exception_list():
    try:
        collection = mongodb.db["awsLoggingUserException"]
        aws_users_collection = mongodb.db["awsUsers"]
        users_collection = mongodb.db["users"]
        query_result = await collection.find().to_list(length=None)

        for user in query_result:
            user["updateTime"] = user["updateTime"].strftime("%Y-%m-%d")

            aws_user = await aws_users_collection.find_one({"UserName": user["_id"]})
            if aws_user and "Groups" in aws_user and aws_user["Groups"]:
                user["groups"] = aws_user["Groups"]
            else:
                user["groups"] = None

            boch_user = await users_collection.find_one({"_id": user["_id"]})  # 이후에 awsAccount로 찾는 것으로 변경하기
            if (
                boch_user
                and "attachedPosition" in boch_user
                and boch_user["attachedPosition"]
            ):
                user["position"] = boch_user["attachedPosition"]
            else:
                user["position"] = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"user_exception_list": query_result})

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/list/exception/member/gcp")
async def get_gcp_member_exception_list():
    try:
        collection = mongodb.db["gcpLoggingMemberException"]
        users_collection = mongodb.db["users"]
        groups_collection = mongodb.db["groups"]
        query_result = await collection.find().to_list(length=None)

        for member in query_result:
            member["updateTime"] = member["updateTime"].strftime("%Y-%m-%d")

            if member["type"] == "user":
                boch_user = await users_collection.find_one({"_id": member["_id"]})  # 이후에 gcpAccount로 찾는 것으로 변경하기
                if (
                    boch_user
                    and "attachedPosition" in boch_user
                    and boch_user["attachedPosition"]
                ):
                    member["position"] = boch_user["attachedPosition"]
                else:
                    member["position"] = None
            elif member["type"] == "group":
                boch_group = await groups_collection.find_one({"groupName": member["_id"]})  # 이후에 gcpGroup으로 찾는 것으로 변경하기
                if (
                    boch_group
                    and "attachedPosition" in boch_group
                    and boch_group["attachedPosition"]
                ):
                    member["position"] = boch_group["attachedPosition"]
                else:
                    member["position"] = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"member_exception_list": query_result})

    return JSONResponse(content=res_json, status_code=200)


@router.delete(path="/delete/exception/user/aws")
async def delete_aws_user_exception(user_name: str):
    try:
        collection = mongodb.db["awsLoggingUserException"]
        query_result = await collection.delete_one({"_id": user_name})
        if query_result.deleted_count == 1:
            return {"message": "user delete success"}
        else:
            raise HTTPException(status_code=500, detail="deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(path="/delete/exception/member/gcp")
async def delete_gcp_member_exception(member_name: str):
    try:
        collection = mongodb.db["gcpLoggingMemberException"]
        query_result = await collection.delete_one({"_id": member_name})
        if query_result.deleted_count == 1:
            return {"message": "member delete success"}
        else:
            raise HTTPException(status_code=500, detail="deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/list/all")
async def get_combined_logging_list():
    try:
        collection = mongodb.db["awsMatchUserAction"]
        pipeline = [
            {"$unwind": "$history"},
            {"$sort": {"history.date": -1, "updateTime": -1}},
            {
                "$lookup": {
                    "from": "awsUserActions",
                    "localField": "history.action",
                    "foreignField": "_id",
                    "as": "action_data",
                }
            },
            {"$unwind": {"path": "$action_data", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "user_name": "$user_name",
                    "date": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$history.date"}
                    },
                    "version": "$history.version",
                    "action_count": {
                        "$size": {"$ifNull": ["$action_data.action_list", []]}
                    },
                    "action_list": "$action_data.action_list",
                }
            },
        ]

        logging_list = await collection.aggregate(pipeline).to_list(None)

        for item in logging_list:
            if not item["action_list"]:
                item["action_list"] = None

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"logging_list": logging_list})

    return JSONResponse(content=res_json, status_code=200)
