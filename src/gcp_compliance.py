from googleapiclient import discovery
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.cloud import logging_v2
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from typing import List

from bson import ObjectId
from .config import settings
from src.database import mongodb
from collections import OrderedDict

import csv
import json


gcp_credentials = service_account.Credentials.from_service_account_info(
    settings.get("gcp_credentials"), scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
gcp_project_id = settings["gcp_credentials"]["project_id"]
gcp_organization_id = settings["gcp_organization_id"]


async def save_admin_activity_to_mongodb(log_list, result):
    collection = mongodb.db["gcpCompliance"]
    current_time = datetime.now().replace(microsecond=0).isoformat()
    data = {
        'type': 'admin_account_usage',
        'date': current_time,
        'result': result,
        'detail': []
    }

    for log in log_list:
        detail_info = {
            'timestamp': log.timestamp.isoformat() if log.timestamp else '',
            'caller_IP': log.payload.get('requestMetadata', {}).get('callerIp', ''),
            'caller_user_agent': log.payload.get('requestMetadata', {}).get('callerSuppliedUserAgent', ''),
            'principal_email': log.payload.get('authenticationInfo', {}).get('principalEmail', ''),
            'permission': ', '.join(auth_info.get('permission', '') for auth_info in log.payload.get('authorizationInfo', [])),
            'service': ', '.join(auth_info.get('resource', '') for auth_info in log.payload.get('authorizationInfo', [])),
            'method': ', '.join(auth_info.get('resource', '') for auth_info in log.payload.get('authorizationInfo', [])),
        }
        data['detail'].append(detail_info)

    query_result = await collection.insert_one(data)

    return str(query_result.inserted_id)


async def get_admin_account_logs(credentials, project_id, admin_email, days_threshold):
    client = logging_v2.Client(credentials=credentials)
    duration = timedelta(days=days_threshold)
    timestamp = (datetime.now() - duration).replace(microsecond=0).isoformat()

    filter_str = (
        f'timestamp>="{timestamp}" '
        f'AND protoPayload.authenticationInfo.principalEmail="{admin_email}"'
    )

    resource_name = f"projects/{project_id}"
    # resource_name = f"organizations/[organization_id]"
    logs = client.list_entries(filter_=filter_str, resource_names=[resource_name])
    log_list = []

    for log in logs:
        log_list.append(log)

    if len(log_list) > 0:
        inserted_id = await save_admin_activity_to_mongodb(log_list, False)

        return False, inserted_id
    else:
        inserted_id = await save_admin_activity_to_mongodb(log_list, True)

        return True, inserted_id
    

async def save_mongodb_to_csv(insert_id):
    collection = mongodb.db["gcpCompliance"]
    document = await collection.find_one({'_id': ObjectId(insert_id)})
    current_date = datetime.now().strftime('%Y%m%d')

    # CSV 파일에 데이터 저장
    csv_filename = f'admin_logs_{current_date}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Timestamp', 'Caller IP', 'Caller User Agent', 'Principal Email', 'Permission', 'Service', 'Method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # CSV 파일 헤더 쓰기
        writer.writeheader()

        # MongoDB에서 가져온 데이터를 CSV 파일에 쓰기
        for detail_info in document['detail']:
            writer.writerow({
                'Timestamp': detail_info['timestamp'],
                'Caller IP': detail_info['caller_IP'],
                'Caller User Agent': detail_info['caller_user_agent'],
                'Principal Email': detail_info['principal_email'],
                'Permission': detail_info['permission'],
                'Service': detail_info['service'],
                'Method': detail_info['method'],
            })


async def get_organization_project_ID(credentials):
    collection = mongodb.db["gcpProjectInfo"]
    service = build('cloudresourcemanager', 'v1', credentials=credentials)

    # 조직 정보 가져오기
    request = service.organizations().search(body={})
    response = await request.execute()

    for organization in response.get('organizations', []):
        organization_data = {
            'type': 'organization',
            'organization_name': organization['displayName'],
            'organization_id': organization['name'].split('/')[-1]
        }
        await collection.insert_one(organization_data)

        # 해당 조직에 속한 프로젝트 정보 가져오기
        project_request = service.projects().list(filter=f"parent.id:{organization['name'].split('/')[-1]} parent.type:organization")
        project_response = await project_request.execute()

        for project in project_response.get('projects', []):
            project_data = {
                'type': 'project',
                'project_name': project['name'],
                'project_id': project['projectId']
            }
            await collection.insert_one(project_data)


def extract_principal_email(entry):
    # entry가 ProtobufEntry이고 payload의 value가 OrderedDict인 경우
    if entry and entry.payload  and isinstance(entry.payload, OrderedDict):
        try:
            # OrderedDict에서 principalEmail 추출
            principal_email = entry.payload.get('authenticationInfo', {}).get('principalEmail')
            return principal_email
        except Exception as e:
            print(f"Error extracting principalEmail: {e}")
    return None


async def get_unused_service_account(credentials, project_id, days_threshold):
    collection = mongodb.db["gcpCompliance"]
    client = logging_v2.Client(credentials=credentials)
    iam_client = build('iam', 'v1', credentials=credentials)
    duration = timedelta(days=days_threshold)
    timestamp = (datetime.now() - duration).replace(microsecond=0).isoformat()
    filter_str = (
        f'timestamp >= "{timestamp}" '
        f'AND protoPayload.authenticationInfo.principalEmail:@{project_id}.iam.gserviceaccount.com'
    )

    # 사용된 서비스 계정 모으기
    used_service_accounts = set()

    # 필터를 사용하여 로그 항목 가져오기
    resource_name = f"projects/{project_id}"
    # resource_name = f"organizations/[organization_id]"
    logs = client.list_entries(filter_=filter_str, resource_names=[resource_name])

    for log in logs:
        principal_email = extract_principal_email(log)
        used_service_accounts.add(principal_email)

    # 모든 서비스 계정 가져오기
    service_accounts = list(iam_client.projects().serviceAccounts().list(name='projects/' + project_id).execute()['accounts'])

    # 사용하지 않은 서비스 계정 찾기
    unused_service_accounts = [account['email'] for account in service_accounts if account['email'] not in used_service_accounts]

    result = len(unused_service_accounts) == 0

    data = {
        "type": "unused_service_account",
        "date": datetime.now(),
        "result": result,
        "detail": unused_service_accounts
    }

    query_result = await collection.insert_one(data)

    return result, str(query_result.inserted_id)


async def disable_unused_service_accounts(credentials, project_id, inserted_id):
    collection = mongodb.db["gcpCompliance"]
    result = await collection.find_one({'_id': inserted_id})

    if result is not None:
        unused_service_accounts = result['detail']

        # 사용하지 않은 서비스 계정 비활성화
        for account_email in unused_service_accounts:
            service = build('iam', 'v1', credentials=credentials)
            await service.projects().serviceAccounts().disable(
                name=f'projects/{project_id}/serviceAccounts/{account_email}',
            ).execute()


async def delete_unused_service_accounts(credentials, project_id, inserted_id):
    collection = mongodb.db["gcpCompliance"]
    result = await collection.find_one({'_id': inserted_id})

    if result is not None:
        unused_service_accounts = result['detail']

        # 사용하지 않은 서비스 계정 삭제
        for account_email in unused_service_accounts:
            service = build('iam', 'v1', credentials=credentials)
            await service.projects().serviceAccounts().delete(
                name=f'projects/{project_id}/serviceAccounts/{account_email}',
            ).execute()


async def disable_unused_service_account_keys(credentials, project_id, inserted_id):
    collection = mongodb.db["gcpCompliance"]
    result = await collection.find_one({'_id': inserted_id})

    if result is not None:
        unused_service_accounts = result['detail']

        # 사용하지 않은 서비스 계정의 키 비활성화
        for account_email in unused_service_accounts:
            service = build('iam', 'v1', credentials=credentials)
            keys = await service.projects().serviceAccounts().keys().list(
                name=f'projects/{project_id}/serviceAccounts/{account_email}'
            ).execute()

            for key in keys['keys']:
                await service.projects().serviceAccounts().keys().disable(
                    name=key['name']
                ).execute()


async def delete_unused_service_account_keys(credentials, project_id, inserted_id):
    collection = mongodb.db["gcpCompliance"]
    result = await collection.find_one({'_id': inserted_id})

    if result is not None:
        unused_service_accounts = result['detail']

        # 사용하지 않은 서비스 계정의 키 삭제
        for account_email in unused_service_accounts:
            service = build('iam', 'v1', credentials=credentials)
            keys = await service.projects().serviceAccounts().keys().list(
                name=f'projects/{project_id}/serviceAccounts/{account_email}'
            ).execute()

            for key in keys['keys']:
                await service.projects().serviceAccounts().keys().delete(
                    name=key['name']
                ).execute()


async def list_keys_without_expiration(credentials, project_id):
    collection = mongodb.db["gcpCompliance"]
    service = build('iam', 'v1', credentials=credentials)
    accounts = await service.projects().serviceAccounts().list(
        name=f'projects/{project_id}'
    ).execute()

    keys_without_expiration = []

    # 모든 서비스 계정을 검사
    for account in accounts['accounts']:
        keys = await service.projects().serviceAccounts().keys().list(
            name=account['name']
        ).execute()

        # 각 계정의 모든 키를 검사
        for key in keys['keys']:
            # 'validBeforeTime' 필드가 없으면 유효기간이 설정되지 않은 것
            if 'validBeforeTime' not in key:
                keys_without_expiration.append({
                    'account': account['email'],
                    'key': key['name']
                })

    result = len(keys_without_expiration) == 0

    data = {
        'type': 'keys_without_expiration',
        'date': datetime.now(),
        'result': result,
        'detail': keys_without_expiration
    }

    query_result = await collection.insert_one(data)

    return result, str(query_result.inserted_id)


async def disable_keys_without_expiration(credentials, inserted_id):
    collection = mongodb.db["gcpCompliance"]
    document = await collection.find_one({'_id': inserted_id})
    
    # 문서의 'detail' 필드에서 유효 기간이 설정되지 않은 서비스 계정 키의 목록을 가져옴
    keys_without_expiration = document['detail']
    
    service = build('iam', 'v1', credentials=credentials)
    
    # 각 키를 비활성화
    for key in keys_without_expiration:
        await service.projects().serviceAccounts().keys().disable(
            name=key['key']
        ).execute()


async def delete_keys_without_expiration(credentials, inserted_id):
    collection = mongodb.db["gcpCompliance"]
    document = await collection.find_one({'_id': inserted_id})
    
    # 문서의 'detail' 필드에서 유효 기간이 설정되지 않은 서비스 계정 키의 목록을 가져옴
    keys_without_expiration = document['detail']
    
    service = build('iam', 'v1', credentials=credentials)
    
    # 각 키를 삭제
    for key in keys_without_expiration:
        await service.projects().serviceAccounts().keys().delete(
            name=key['key']
        ).execute()


async def check_key_rotation(credentials, project_id, days_threshold):
    collection = mongodb.db["gcpCompliance"]
    service = build('iam', 'v1', credentials=credentials)
    service_accounts = await service.projects().serviceAccounts().list(
        name=f'projects/{project_id}'
    ).execute()

    old_keys = []

    for account in service_accounts['accounts']:
        keys = await service.projects().serviceAccounts().keys().list(
            name=account['name']
        ).execute()

        for key in keys['keys']:
            # Convert string to datetime
            key_created_at = parse(key['validAfterTime'])

            # Calculate the age of the key
            key_age = datetime.now(timezone.utc) - key_created_at

            # If the key is older than the threshold, delete it
            if key_age > timedelta(days=days_threshold):
                old_keys.append({'account': account['email'], 'key': key['name']})
    
    result = not bool(old_keys)

    query_result = await collection.insert_one({
        'type': 'check_key_rotation',
        'date': datetime.now(),
        'result': result,
        'detail': old_keys
    })

    return result, str(query_result.inserted_id)


async def renew_old_keys(credentials, inserted_id):
    collection = mongodb.db["gcpCompliance"]
    document = await collection.find_one({'_id': inserted_id})

    # 'detail' 필드에서 기간이 지난 서비스 계정 키의 목록을 가져옴
    old_keys = document['detail']

    service = build('iam', 'v1', credentials=credentials)

    # 각 키를 갱신
    for key in old_keys:
        account_email = key['account']
        # 새 키 생성
        await service.projects().serviceAccounts().keys().create(
            name=f'projects/-/serviceAccounts/{account_email}',
            body={}
        ).execute()


async def count_admins(credentials, project_id):
    collection = mongodb.db["gcpCompliance"]
    service = build('cloudresourcemanager', 'v1', credentials=credentials)
    policy = await service.projects().getIamPolicy(
        resource=project_id,
        body={}
    ).execute()

    admins = []
    for binding in policy['bindings']:
        # 관리자 권한을 가진 구성원들만 골라냄
        if 'roles/owner' in binding['role']:
            for member in binding['members']:
                admins.append(member)
    
    result = len(admins) < 2

    query_result = await collection.insert_one({
        'type': 'count_admins',
        'project': project_id,
        'date': datetime.now(),
        'result': result,
        'detail': admins
    })

    return result, str(query_result.inserted_id)
