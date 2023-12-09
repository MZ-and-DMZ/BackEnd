import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from src.boto3_connect import aws_sdk
from src.database import mongodb
from src.utils import bson_to_json

from googleapiclient.discovery import build

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


def get_all_roles_for_member(cloudresourcemanager_service, project_id, member):
    policy = cloudresourcemanager_service.projects().getIamPolicy(resource=project_id, body={}).execute()

    roles_for_member = []
    for binding in policy['bindings']:
        if member in binding['members']:
            roles_for_member.append(binding['role'])

    return roles_for_member


def remove_role_binding(cloudresourcemanager_service, project_id, member, role):
    policy = cloudresourcemanager_service.projects().getIamPolicy(resource=project_id, body={}).execute()

    for binding in policy['bindings']:
        if binding['role'] == role and member in binding['members']:
            binding['members'].remove(member)
            break

    response = cloudresourcemanager_service.projects().setIamPolicy(
        resource=project_id,
        body={
            'policy': policy
        }).execute()
    
    print(response)


def create_and_assign_role(iam_service, cloudresourcemanager_service, project_id, member, current_time, permissions):
    member_name = member.split('@')[0].replace(':', '_')
    role_id = 'boch_' + member_name

    # 역할 생성
    iam_service.projects().roles().create(
        parent=f'projects/{project_id}',
        body={
            'roleId': role_id,
            'role': {
                'title': 'Optimization Role - Boch ' + member_name,
                'description': 'Optimization role for ' + member_name + '(' + current_time.strftime('%Y-%m-%d') + ')',
                'includedPermissions': permissions,
                'stage': 'GA'
            }
        }).execute()

    # 역할 부여
    policy = cloudresourcemanager_service.projects().getIamPolicy(resource=project_id, body={}).execute()

    policy['bindings'].append({
        'role': f'projects/{project_id}/roles/{role_id}',
        'members': [member]
    })

    cloudresourcemanager_service.projects().setIamPolicy(
        resource=project_id,
        body={
            'policy': policy
        }).execute()


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
            iam_service = build('iam', 'v1', credentials=credentials)
            cloudresourcemanager_service = build('cloudresourcemanager', 'v1', credentials=credentials)

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
            all_roles = await get_all_roles_for_member(cloudresourcemanager_service, project_id, member)  # 이후에 src 폴더 안으로 이동

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
                target_role = [f"projects/{project_id}/roles/{role_id}"]
                if permissions:
                    # 역할 수정, optimizationVersion 수정(현재 버전)
                    existing_role = await iam_service.projects().roles().get(name=f'projects/{project_id}/roles/{role_id}').execute()
                    existing_role['role']['includedPermissions'] = permissions
                    existing_role['role']['description'] = 'Optimization role for ' + user_name + '(' + current_time.strftime('%Y-%m-%d') + ')'
                    await iam_service.projects().roles().patch(
                        name=f'projects/{project_id}/roles/{role_id}',
                        body=existing_role
                    ).execute()
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
                    await remove_role_binding(cloudresourcemanager_service, project_id, member, f'projects/{project_id}/roles/{role_id}')  # 이후에 src 폴더 안으로 이동
                    await iam_service.projects().roles().delete(name=f'projects/{project_id}/roles/{role_id}').execute()
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
                    await create_and_assign_role(iam_service, cloudresourcemanager_service, project_id, member, current_time, permissions)  # 이후에 src 폴더 안으로 이동
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


# gcp previous_role 롤백 함수 (이후에 logging_gcp로 이동)
@router.post(path="/rollback/previous/{member_name}")
async def logging_rollback(version: int, member_name: str = Path(..., title="member name")):
    try:
        iam_service = build('iam', 'v1', credentials=credentials)
        cloudresourcemanager_service = build('cloudresourcemanager', 'v1', credentials=credentials)

        gcp_match_collection = mongodb.db["gcpMatchMemberPermission"]
        gcp_permission_collection = mongodb.db["gcpMemberPermissions"]
        gcp_role_collection = mongodb.db["gcpCustomerRole"]

        query_result = await gcp_match_collection.find_one({"member_name": member_name})
        member = query_result["member"]
        selected_record = query_result["history"][version - 1]
        selected_previous_role = selected_record["previous_role"]
        role_id = 'boch_' + member_name
        current_time = datetime.now()
        all_roles = await get_all_roles_for_member(cloudresourcemanager_service, project_id, member)  # 이후에 src 폴더 안으로 이동

        # # previous_role에 커스텀 역할이 있는지 확인
        # for role in selected_previous_role:
        #     if not role.startswith('roles/'):
        #         # 최적화로 생성된 역할인지 아닌지 확인
        #         if 'boch_' + member_name in role:
        #             # 구성원에게 boch_{member} 역할이 붙어있는지 아닌지 확인
        #             if any('boch_' + member_name in role for role in all_roles):
        #                 # 선택한 버전 이전의 boch_{member} 역할로 수정
        #             else:
        #                 # 선택한 버전 이전의 boch_{member} 역할 생성 후 붙이기
        #         else:
        #             # gcp에 해당 역할이 존재하는지 확인
        #             # 없다면 db에서 해당 역할 찾아서 역할 만들기
        
        # previous_role과 all_roles 비교
        # previous_role에만 있는 것 (boch_{member} 역할 제외) : 역할 바인딩 추가 (attach_role)
        # all_roles에만 있는 것 : 역할 바인딩 삭제 (detach_role)

        return {"message": "previous version rollback success"}
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
