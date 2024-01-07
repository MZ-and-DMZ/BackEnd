from googleapiclient import discovery
from google.oauth2 import service_account
from google.cloud import logging
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from typing import List

from bson import ObjectId
from .config import settings
from src.database import mongodb

import csv


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

    collection.insert_one(data)

    return str(result.inserted_id)


async def get_admin_account_logs(credentials, project_id, admin_email, days_threshold):
    client = logging.Client(credentials=credentials)
    duration = timedelta(days=days_threshold)
    timestamp = (datetime.now() - duration).replace(microsecond=0).isoformat()

    filter_str = (
        f'timestamp>="{timestamp}" '
        f'AND protoPayload.authenticationInfo.principalEmail="{admin_email}"'
    )

    resource_name = f"projects/{project_id}"
    logs = client.list_entries(filter_=filter_str, resource_names=[resource_name])
    log_list = []

    for log in logs:
        log_list.append(log)

    if len(log_list) > 0:
        inserted_id = await save_admin_activity_to_mongodb(log_list, False)

        return True, log_list, inserted_id
    else:
        inserted_id = await save_admin_activity_to_mongodb(log_list, True)

        return False, log_list, inserted_id
    

async def save_mongodb_to_csv(insert_id):
    collection = mongodb.db["gcpCompliance"]
    document = collection.find_one({'_id': ObjectId(insert_id)})
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