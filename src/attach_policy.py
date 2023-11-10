from models import mongodb

from .boto3_connect import aws_sdk


async def find_aws_account(user_name: str):
    collection = mongodb.db["users"]
    find_result = await collection.find_one({"_id": user_name})
    return find_result["awsAccount"]


async def find_policies(position_name: str):
    collection = mongodb.db["positionLink"]
    find_result = await collection.find_one({"_id": position_name})
    return find_result["arns"]


async def attach_policy(user_name: str, position_name: str):
    aws_account = await find_aws_account(user_name=user_name)
    policy_arns = await find_policies(position_name=position_name)

    aws_sdk.iam_connect()
    for arn in policy_arns:
        aws_sdk.client.attach_user_policy(UserName=aws_account, PolicyArn=arn)
    aws_sdk.iam_close()


async def detach_policy(user_name: str, position_name: str):
    aws_account = await find_aws_account(user_name=user_name)
    policy_arns = await find_policies(position_name=position_name)

    aws_sdk.iam_connect()
    for arn in policy_arns:
        aws_sdk.client.detach_user_policy(UserName=aws_account, PolicyArn=arn)
    aws_sdk.iam_close()
