import boto3
import pprint
import pytz
import pandas as pd
import os
import datetime
from .aws_sdk_connect import aws_sdk


# IAM-1 root 계정의 ACCESS-KEY 활성화 여부 확인
async def check_root_key_from_credential_report():
    """
    반환 : root 계정의 액세스키 사용 여부 확인 boolean
    """
    aws_sdk.iam_connect()
    response = aws_sdk.client.generate_credential_report()
    response = aws_sdk.client.get_credential_report()

    result = False

    with open("credential_report.csv", "wb") as f:
        f.write(response["Content"])

    with open("credential_report.csv", "r") as f:
        df = pd.read_csv("credential_report.csv", sep=",", header=0)

        df = df[["arn", "access_key_1_active", "access_key_2_active"]]
        row_count = df.shape[0]

        for cnt in range(row_count) :
            if df.loc[cnt, "access_key_1_active"] or df.loc[cnt, "access_key_2_active"] :
                if df.loc[cnt, "arn"].split(":")[-1] == "root" :
                    result = True
                else :
                    pass
            else :
                pass

    file = "credential_report.csv"
    os.remove(file)
    aws_sdk.iam_close()

    return result


# IAM-2 root 계정 사용 여부 확인
async def get_account_id():
    """
    반환 : 계정 번호(12자리 정수)
    """
    sts_client = boto3.client('sts')
    response = sts_client.get_caller_identity()
    account_id = response['Account']

    return account_id


async def check_root_account_usage(account_id):
    """
    root 계정 활성화 여부 boolean
    """
    # AWS 서비스 클라이언트 생성
    client = boto3.client('organizations')
    active = False

    try:
        # AWS 계정 정보 조회
        response = client.describe_account(AccountId=account_id)
        account_status = response['Account']['Status']
        pprint.pprint(response)

        if account_status == 'ACTIVE':
            active = True
        else:
            print("Root account is not active. Status:", account_status)

        return active

    except Exception as e:
        print("Error:", str(e))


# IAM -3 액세스키 사용 현황 확인
# 사용자별 액세스키 현황
async def get_all_users_keys() -> list:
    """
    반환 : { "user" : username, "keys" : [ user_key1, ... ] }를 요소로 갖는 배열
    """
    iam = boto3.client("iam")
    users = iam.list_users()
    all_user_key = []

    for user in users["Users"]:
        username = user["UserName"]
        user_key = []
        access_keys = iam.list_access_keys(UserName=username)["AccessKeyMetadata"]
        for access_key_metadata in access_keys :
            user_key.append(access_key_metadata["AccessKeyId"])
        user_key = { "user" : username, "keys" : user_key }
        all_user_key.append(user_key)

    return all_user_key


# 액세스키별 마지막 사용 날짜와 오늘 날짜의 차이
async def check_last_used_date_access_key(access_key) -> int :
    """
    입력 : 액세스키
    반환 : 액세스키의 마지막 사용 날짜와 오늘 날짜의 차이
    """
    iam_client = boto3.client("iam")
    access_key_id = access_key 
    last_used_date = iam_client.get_access_key_last_used(AccessKeyId=access_key_id)
    try : 
        last_used_date = last_used_date['AccessKeyLastUsed']['LastUsedDate']
        korea_tz = pytz.timezone("Asia/Seoul")
        last_used_date = last_used_date.astimezone(korea_tz)
        today = datetime.datetime.today().astimezone(korea_tz)
    
        diff = today - last_used_date
        diff = diff.days
    except KeyError as e:
        diff = 0
    
    return diff


# 사용자별 액세스키, 날짜 차이 반환
async def check_user_access_key_date() -> list :
    """
    반환 값 : {"user" : user, "key" : key, "diff_day" : diff_day} 으로 이루어진 배열
    user : 사용자명
    key : 액세스 키
    diff_day : 오늘 날짜 - 마지막 사용날짜
    """
    all_user_key = get_all_users_keys()
    all_user_key_diff = []

    for user_key in all_user_key :
        user = user_key["user"]
        for key in user_key["keys"] :
            diff_day = check_last_used_date_access_key(key)
            user_key_diff = {"user" : user, "key" : key, "diff_day" : diff_day}
            all_user_key_diff.append(user_key_diff)

    return all_user_key_diff


# IAM -4 Access key 주기적 변경
# 만료된 액세스 키 관련 정보 확인
async def find_expired_access_key(duration) -> list :
    """
    반환 : 만료된 키에 대한 정보({user : 사용자명, key: 키명, diff : 차이점})
    """
    user_key_diffs = check_user_access_key_date()
    expired_keys = []
    for user_key_diff in user_key_diffs :
        if user_key_diff["diff"] >= duration :
            expired_keys.append(user_key_diff)
        else :
            pass
    return user_key_diffs


# 신규 액세스 키 생성
async def create_new_access_key(username) -> dict :
    """
    반환 : 신규 생성한 액세스 키 관련 데이터
    """
    iam = boto3.client("iam")
    new_access_key = iam.create_access_key(UserName=username)['AccessKey']['AccessKeyId']
    return new_access_key


# 기존 액세스 키 삭제
async def delete_access_key(access_key_id) -> bool:
    """
    반환 : bool
    액세스키를 입력받고 정상 삭제 여부 True, False 확인
    """
    iam = boto3.client("iam")
    try : 
        iam.delete_access_key(access_key_id=access_key_id)
        return True
    except :
        return False


# (종합) 만료된 액세스 키 확인, 삭제, 신규 생성
async def update_access_key(duration) :
    expired_keys = find_expired_access_key(duration=duration)
    for expired_key in expired_keys :
        if delete_access_key(expired_key["key"]) :
            new_access_key = create_new_access_key(expired_key["user"])
        else :
            print("Something goes wrong...")


# IAM -6 비밀번호 복잡도 및 변경 주기 설정
async def password_policy(length=8, MaxAge=90) :
    """
    반환값 : 없음
    그냥 다 True, 최소 8글자 이상, 90일 이상 사용 불가 
    """
    iam = boto3.client("iam")
    response = iam.update_account_password_policy(
        MinimumPasswordLength=8,
        RequireSymbols=True,
        RequireNumbers=True,
        RequireUppercaseCharacters=True,
        RequireLowercaseCharacters=True,
        AllowUsersToChangePassword=True,
        MaxPasswordAge=90,
        PasswordReusePrevention=90,
        HardExpiry=True
    )