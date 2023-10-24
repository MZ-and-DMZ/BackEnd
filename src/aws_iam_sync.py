from pymongo import MongoClient

from database import db_client

from .aws_iam import awsSdk
from .config import conf


class awsIamSync:
    def __init__(self):
        self.client = MongoClient(conf["DB_server"], serverSelectionTimeoutMS=5000)
        self.db = self.client["Boch"]
        self.aws_sdk = awsSdk()
        pass

    # 직무를 aws iam 계정에 할당
    def position_sync_aws(self, aws_iam_user_name, position_name):
        collection = self.db["positions"]
        query_result = collection.find_one({"positionName": position_name})
        for policy_arn in list(query_result["policies"].value()):
            self.aws_sdk.attach_user_policy(aws_iam_user_name, policy_arn)

    def user_create_sync(self, user_data):
        collection = self.db["awsUsers"]
        query_result = collection.find_one({"userName": user_data.awsAccount})
        if query_result is None:
            raise Exception("aws iam 계정이 없음")
        for postion_name in user_data.attachedPosition:
            self.position_sync_aws(user_data.awsAccount, postion_name)
        pass
