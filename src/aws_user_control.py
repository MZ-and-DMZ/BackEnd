from src.database import mongodb

from .aws_sdk_connect import aws_sdk


async def create_user(user_name: str):
    aws_sdk.iam_connect()
    aws_sdk.client.create_user(UserName=user_name)
    aws_sdk.iam_close()


async def attach_mfa_policy(user_name: str):
    arn = "arn:aws:iam::481280410531:policy/forceMfa"
    aws_sdk.iam_connect()
    aws_sdk.client.attach_user_policy(UserName=user_name, PolicyArn=arn)
    aws_sdk.iam_close()
