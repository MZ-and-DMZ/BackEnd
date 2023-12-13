import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json

from googleapiclient.discovery import build
from src.gcp_logging_control import gcp_credentials, gcp_project_id, get_all_roles_for_member, remove_role_binding, add_role_binding, create_and_assign_role, update_optimization_role, create_customer_role, get_project_role_list

router = APIRouter(prefix="/logging/gcp", tags=["logging gcp"])


@router.post(path="/set/duration")
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


@router.get(path="/get/duration")
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


@router.post(path="/add/exception/member")
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


@router.get(path="/list/exception/member")
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


@router.delete(path="/delete/exception/member")
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


@router.post(path="/rollback/previous/{member_name}")
async def logging_rollback(version: int, member_name: str = Path(..., title="member name")):
    try:
        iam_service = build('iam', 'v1', credentials=gcp_credentials)
        cloudresourcemanager_service = build('cloudresourcemanager', 'v1', credentials=gcp_credentials)

        gcp_match_collection = mongodb.db["gcpMatchMemberPermission"]
        gcp_permission_collection = mongodb.db["gcpMemberPermissions"]
        gcp_role_collection = mongodb.db["gcpCustomerRole"]

        query_result = await gcp_match_collection.find_one({"member_name": member_name})
        member = query_result["member"]
        selected_record = query_result["history"][version - 1]
        updated_version = query_result["history"][-1]["version"] + 1
        selected_last_refresh_time = selected_record["last_refresh_time"]
        selected_previous_role = selected_record["previous_role"]
        selected_date = selected_record["date"]
        role_id = 'boch_' + member_name
        current_time = datetime.now()
        all_roles = await get_all_roles_for_member(cloudresourcemanager_service, gcp_project_id, member)

        # previous_role에 커스텀 역할이 있는지 확인
        for role in selected_previous_role:
            if not role.startswith('roles/'):
                # 최적화로 생성된 역할인지 아닌지 확인
                if 'boch_' + member_name in role:
                    previous_record = query_result["history"][version - 2]
                    previous_id = previous_record["permission"]
                    previous_permission = await gcp_permission_collection.find_one({"_id": previous_id})
                    permissions = previous_permission['permission_list']

                    if 'optimization_base' in previous_record:
                        previous_optimization_base = previous_record["optimization_base"] - 1
                        optimization_base_record = query_result["history"][previous_optimization_base]
                        optimization_base_id = optimization_base_record["permission"]
                        optimization_base_permission = await gcp_permission_collection.find_one({"_id": optimization_base_id})
                        permissions = list(set(permissions + optimization_base_permission['permission_list']))

                        permission_query_result = await gcp_permission_collection.insert_one({
                            "member_name": member_name,
                            "date": current_time,
                            "permission_list": sorted(permissions)
                        })
                        previous_id = permission_query_result.inserted_id
                    
                    # 구성원에게 boch_{member} 역할이 붙어있는지 아닌지 확인
                    if any('boch_' + member_name in role for role in all_roles):
                        if permissions:
                            # 선택한 버전 이전의 boch_{member} 역할로 수정
                            await update_optimization_role(iam_service, gcp_project_id, member_name, current_time, permissions, role_id)
                        else:
                            await remove_role_binding(cloudresourcemanager_service, gcp_project_id, member, role)
                            await iam_service.projects().roles().delete(name=role).execute()
                            await gcp_match_collection.update_one(
                                {"member_name": member_name},
                                {
                                    "$unset": {
                                        "optimizationVersion": ""
                                    }
                                }
                            )
                    else:
                        if permissions:
                            # 선택한 버전 이전의 boch_{member} 역할 생성 후 붙이기
                            await create_and_assign_role(iam_service, cloudresourcemanager_service, gcp_project_id, member, current_time, permissions)
                            await gcp_match_collection.update_one(
                                {"member_name": member_name},
                                {
                                    "$set": {
                                        "optimizationVersion": updated_version
                                    }
                                }
                            )
                else:
                    # gcp에 해당 역할이 존재하는지 확인
                    roles_list = await get_project_role_list(iam_service, gcp_project_id)

                    if not any(role_info['name'] == role for role_info in roles_list.get('roles', [])):
                        # db에서 해당 역할 찾아서 역할 만들기
                        role_document = await gcp_role_collection.find_one({"_id": role})
                        # history 객체 중 date가 selected_date를 넘지 않고 가장 가까운 객체 찾기
                        closest_history = min(
                            (history for history in role_document["history"] if history["date"] <= selected_date),
                            key=lambda x: selected_date - x["date"],
                            default=None
                        )
                        selected_role_id = role.split("/")[-1]
                        await create_customer_role(iam_service, gcp_project_id, selected_role_id, closest_history)
                        
                        if role_document['history'][-1]['includedPermissions'] != closest_history['includedPermissions']:
                            await gcp_role_collection.update_one(
                                {'_id': role},
                                {"$push": {
                                    'history': {
                                        'title': closest_history["title"],
                                        'description': closest_history["description"],
                                        'includedPermissions': closest_history["includedPermissions"],
                                        'date': current_time
                                    }
                                }}
                            )
        
        attach_roles = [role for role in selected_previous_role if role not in all_roles and 'boch_' + member_name not in role]
        detach_roles = [role for role in all_roles if role not in selected_previous_role]

        for role in attach_roles:
            await add_role_binding(cloudresourcemanager_service, gcp_project_id, member, role)

        for role in detach_roles:
            await remove_role_binding(cloudresourcemanager_service, gcp_project_id, member, role)

        await gcp_match_collection.update_one(
            {"member_name": member_name},
            {
                '$push': {
                    'history': {
                        'date': current_time,   # 현재 시간
                        'permission': previous_id,
                        'previous_role': all_roles, # 현재 붙어있는 역할 목록
                        'target_role': all_roles,
                        'last_refresh_time': selected_last_refresh_time,    # 선택한 버전의 시간
                        'version': updated_version  # 마지막 버전 + 1
                    }
                },
                "$set": {
                    "updateTime": current_time  # 현재 시간
                },
            }
        )

        return {"message": "previous version rollback success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
