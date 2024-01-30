from src.database import mongodb

from .aws_sdk_connect import aws_sdk

async def create_user(user_name: str):
    aws_sdk.iam_connect()
    aws_sdk.client.create_user(UserName=user_name)
    aws_sdk.iam_close()