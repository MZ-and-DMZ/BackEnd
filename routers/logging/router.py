import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from src.boto3_connect import aws_sdk
from src.database import mongodb
from src.utils import bson_to_json

from googleapiclient.discovery import build
from src.gcp_logging_control import gcp_credentials, gcp_project_id, get_all_roles_for_member, remove_role_binding, create_and_assign_role, update_optimization_role

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
async def logging_rollback(version: int, csp: str, user_name: str = Path(..., title="user name")):
    try:
        if csp == "aws":
            aws_sdk.iam_connect()
            iam_client = aws_sdk.client
            aws_match_collection = mongodb.db["awsMatchUserAction"]
            query_result = await aws_match_collection.find_one({"user_name": user_name})

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

            await aws_match_collection.update_one(
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
        elif csp == "gcp":
            # gcp 연결 - iam, cloudresourcemanager (credentials 설정)
            iam_service = build('iam', 'v1', credentials=gcp_credentials)
            cloudresourcemanager_service = build('cloudresourcemanager', 'v1', credentials=gcp_credentials)

            gcp_match_collection = mongodb.db["gcpMatchMemberPermission"]
            gcp_permission_collection = mongodb.db["gcpMemberPermissions"]

            query_result = await gcp_match_collection.find_one({"member_name": user_name})
            member = query_result["member"]
            selected_record = query_result["history"][version - 1]
            updated_version = query_result["history"][-1]["version"] + 1
            selected_last_refresh_time = selected_record["last_refresh_time"]
            selected_id = selected_record["permission"]
            selected_permission = await gcp_permission_collection.find_one({"_id": selected_id})
            permissions = selected_permission['permission_list']
            role_id = 'boch_' + user_name
            current_time = datetime.now()
            all_roles = await get_all_roles_for_member(cloudresourcemanager_service, gcp_project_id, member)

            if 'optimization_base' in selected_record:
                # 해당 optimization_base의 권한 목록을 가져와 중복 없이 합치기, permission 컬렉션에 저장 (id 저장)
                selected_optimization_base = selected_record["optimization_base"] - 1
                optimization_base_record = query_result["history"][selected_optimization_base]
                optimization_base_id = optimization_base_record["permission"]
                optimization_base_permission = await gcp_permission_collection.find_one({"_id": optimization_base_id})
                permissions = list(set(permissions + optimization_base_permission['permission_list']))

                permission_query_result = await gcp_permission_collection.insert_one({
                    "member_name": user_name,
                    "date": current_time,
                    "permission_list": sorted(permissions)
                })
                selected_id = permission_query_result.inserted_id

            # 구성원에게 boch_{member} 역할이 붙어있는지 아닌지 확인
            if any('boch_' + user_name in role for role in all_roles):
                target_role = [f"projects/{gcp_project_id}/roles/{role_id}"]
                if permissions:
                    # 역할 수정, optimizationVersion 수정(현재 버전)
                    await update_optimization_role(iam_service, gcp_project_id, user_name, current_time, permissions, role_id)
                    await gcp_match_collection.update_one(
                        {"member_name": user_name},
                        {
                            "$set": {
                                "optimizationVersion": updated_version
                            }
                        }
                    )
                else:
                    # 역할 바인딩 해제 및 삭제, optimizationVersion 지우기
                    await remove_role_binding(cloudresourcemanager_service, gcp_project_id, member, f'projects/{gcp_project_id}/roles/{role_id}')
                    await iam_service.projects().roles().delete(name=f'projects/{gcp_project_id}/roles/{role_id}').execute()
                    await gcp_match_collection.update_one(
                        {"member_name": user_name},
                        {
                            "$unset": {
                                "optimizationVersion": ""
                            }
                        }
                    )
            else:
                target_role = []
                if permissions:
                    # 역할 생성, optimizationVersion 설정(현재 버전)
                    await create_and_assign_role(iam_service, cloudresourcemanager_service, gcp_project_id, member, current_time, permissions)
                    await gcp_match_collection.update_one(
                        {"member_name": user_name},
                        {
                            "$set": {
                                "optimizationVersion": updated_version
                            }
                        }
                    )
            
            await gcp_match_collection.update_one(
                {"member_name": user_name},
                {
                    '$push': {
                        'history': {
                            'date': current_time,   # 현재 시간
                            'permission': selected_id,  # 선택한 버전의 권한 목록 (optimization_base이 있다면 새로 추가된 permission 컬렉션의 id)
                            'previous_role': all_roles, # 현재 붙어있는 역할 목록
                            'target_role': target_role, # 역할 존재 시 boch_{member}, 아니라면 []
                            'last_refresh_time': selected_last_refresh_time,    # 선택한 버전의 시간
                            'version': updated_version  # 마지막 버전 + 1
                        }
                    },
                    "$set": {
                        "updateTime": current_time  # 현재 시간
                    },
                }
            )
        return {"message": "rollback success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/list/all")
async def get_combined_logging_list():
    try:
        # AWS data
        awsCollection = mongodb.db["awsMatchUserAction"]
        awsPipeline = [
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
                    "updateTime": "$updateTime",
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

        awsLoggingList = await awsCollection.aggregate(awsPipeline).to_list(None)

        for item in awsLoggingList:
            if not item["action_list"]:
                item["action_list"] = None
            item["csp"] = "aws"

        # GCP data
        gcpCollection = mongodb.db["gcpMatchMemberPermission"]
        gcpPipeline = [
            {"$unwind": "$history"},
            {"$sort": {"history.date": -1, "updateTime": -1}},
            {
                "$lookup": {
                    "from": "gcpMemberPermissions",
                    "localField": "history.permission",
                    "foreignField": "_id",
                    "as": "permission_data",
                }
            },
            {"$unwind": {"path": "$permission_data", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "member_name": "$member_name",
                    "updateTime": "$updateTime",
                    "date": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$history.date"}
                    },
                    "version": "$history.version",
                    "permission_count": {
                        "$size": {"$ifNull": ["$permission_data.permission_list", []]}
                    },
                    "permission_list": "$permission_data.permission_list",
                }
            },
        ]

        gcpLoggingList = await gcpCollection.aggregate(gcpPipeline).to_list(None)

        for item in gcpLoggingList:
            if not item["permission_list"]:
                item["permission_list"] = None
            item["csp"] = "gcp"

        # Combine and sort
        loggingList = awsLoggingList + gcpLoggingList
        loggingList.sort(key=lambda x: (x["date"], x["updateTime"]), reverse=True)

        for item in loggingList:
            del item["updateTime"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = bson_to_json({"logging_list": loggingList})

    return JSONResponse(content=res_json, status_code=200)
