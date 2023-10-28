import boto3

from fastapi import HTTPException
from pymongo import MongoClient
from database import db_client
from .config import conf


class awsSDK:
    def __init__(self):
        self.aws_sdk = boto3.client(
            "iam",
            aws_access_key_id=conf["aws_access_key"],
            aws_secret_access_key=conf["aws_secret_access_key"],
        )
        # self.client = MongoClient(conf["DB_server"], serverSelectionTimeoutMS=5000)
        # self.db = self.client["Boch"]
        # self.users_collection = self.db["users"]
        # self.groups_collection = self.db["groups"]
        # self.policies_collection = self.db["policies"]
        # self.awsUsers_collection = self.db["awsUsers"]
        # self.awsGroups_collection = self.db["awsGroups"]
        # self.awsPolicies_collection = self.db["awsPolicies"]

    def create_group(self, group_name):
        return self.aws_sdk.create_group(GroupName=group_name)

    def add_user_to_group(self, group_name, user_name):
        return self.aws_sdk.add_user_to_group(UserName=user_name, GroupName=group_name)

    def attach_group_policy(self, group_name, policy_arn):
        return self.aws_sdk.attach_group_policy(
            GroupName=group_name, PolicyArn=policy_arn)

    def attach_group_position(group_name, position_id):
        pass

    def update_awsUsers(user_name):
        pass

    def update_awsGroups(group_name):
        pass