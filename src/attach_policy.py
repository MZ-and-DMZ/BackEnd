from models import mongodb

from .boto3_connect import aws_sdk


def find_aws_account(user_name: str):
    collection = mongodb.db["users"]
    find_result = collection.find_one({"_id": user_name})
    return find_result["awsAccount"]


def find_policies(position_name: str):
    collection = mongodb.db["positionLink"]
    find_result = collection.find_one({"_id": position_name})
    return find_result["arns"]


def attach_policy(user_name: str, position_name: str):
    aws_account = find_aws_account(user_name=user_name)
    policy_arns = find_policies(position_name=position_name)

    aws_sdk.iam_connect()
    for arn in policy_arns:
        aws_sdk.client.attach_user_policy(UserName=aws_account, PolicyArn=arn)
    aws_sdk.iam_close()


def detach_policy(user_name: str, position_name: str):
    aws_account = find_aws_account(user_name=user_name)
    policy_arns = find_policies(position_name=position_name)

    aws_sdk.iam_connect()
    for arn in policy_arns:
        aws_sdk.client.detach_user_policy(UserName=aws_account, PolicyArn=arn)
    aws_sdk.iam_close()
