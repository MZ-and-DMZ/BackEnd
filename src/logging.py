import requests
import boto3

from fastapi.responses import JSONResponse
from .config import conf


# 주어진 url에서 파일 크기를 가져오기
def get_file_size(url):
    response = requests.head(url)
    if 'content-length' in response.headers:
        return int(response.headers['content-length'])
    return None


# aws action list 업데이트
def download_and_update_actions(size_collection, collection):
    github_url = "https://raw.githubusercontent.com/TryTryAgain/aws-iam-actions-list/master/all-actions.txt"
    current_file_size = get_file_size(github_url)  # 현재 파일 크기 가져오기

    size_result = size_collection.find_one({"fileName": github_url})  # 기존의 fileSize 검색

    if size_result is not None:
        previous_file_size = size_result.get("fileSize")
    else:
        previous_file_size = None

    if current_file_size != previous_file_size:  # 현재의 파일 크기와 DB의 파일 크기가 다른 경우
        collection.delete_many({})  # DB 데이터 삭제
        response = requests.get(github_url)
        if response.status_code == 200:
            actions = response.text.split("\n")
            service_action_dict = {}

            for action in actions:
                parts = action.strip().split(":")
                if len(parts) == 2:
                    service, action_name = parts
                    if service not in service_action_dict:
                        service_action_dict[service] = []
                    service_action_dict[service].append(f"{service}:{action_name}")

            for service, action_list in service_action_dict.items():
                document = {
                    "serviceName": service,
                    "actionList": action_list
                }
                collection.insert_one(document)

            if size_result is not None:
                size_collection.update_one({"fileName": github_url}, {"$set": {"fileSize": current_file_size}})
            else:
                size_collection.insert_one({"fileName": github_url, "fileSize": current_file_size})

            return JSONResponse(content={"message": "actions updated successfully"}, status_code=200)
    else:
        return JSONResponse(content={"message": "update is not needed"}, status_code=200)


# 사용자에게 부여된 정책을 가져오기
def get_user_policy_document(iam, user_arn):
    response = iam.list_attached_user_policies(UserName=user_arn.split('/')[-1])
    user_policies = response['AttachedPolicies']

    inline_policies = iam.list_user_policies(UserName=user_arn.split('/')[-1])
    user_policies.extend(inline_policies['PolicyNames'])

    return user_policies


# 사용자가 속한 그룹에 부여된 정책을 가져오기
def get_group_policy_document(iam, user_arn):
    response = iam.list_groups_for_user(UserName=user_arn.split('/')[-1])
    group_policies = []

    for group in response['Groups']:
        group_name = group['GroupName']
        group_attached_policies = iam.list_attached_group_policies(GroupName=group_name)
        group_policies.extend(group_attached_policies['AttachedPolicies'])

        group_inline_policies = iam.list_group_policies(GroupName=group_name)
        group_policies.extend([f'{group_name}:{policy}' for policy in group_inline_policies['PolicyNames']])

    return group_policies


def get_user_policies(user_arn):
    iam = boto3.client("iam", 
                       aws_access_key_id=conf["aws_access_key"], 
                       aws_secret_access_key=conf["aws_secret_access_key"])
    
    user_policies = get_user_policy_document(iam, user_arn)
    group_policies = get_group_policy_document(iam, user_arn)
    
    print(user_policies)
    print(group_policies)

