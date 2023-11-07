import json
import re

import boto3
from fastapi import HTTPException
from pymongo import MongoClient

from . import util
from .config import conf


class awsIamSync:
    def __init__(self):
        self.iam_sdk = boto3.client(
            "iam",
            aws_access_key_id=conf["aws_access_key"],
            aws_secret_access_key=conf["aws_secret_access_key"],
        )
        self.client = MongoClient(conf["DB_server"], serverSelectionTimeoutMS=5000)
        self.db = self.client["Boch"]
        self.positions_collection = self.db["positions"]
        self.awsPolicies_collection = self.db["awsPolicies"]
        self.awsUsers_collection = self.db["awsUsers"]

    # 정책을 합쳐준다.
    def policy_compress(self, policies):
        result_docs_list = []
        string_length = []
        for policy in policies:
            string_length.append(util.count_string(policy["Statement"]))
        index_set = util.calculate_set(string_length)
        for set in index_set:
            if isinstance(set, int):
                result_docs_list.append(set)
                continue
            result_docs = {"Version": "2012-10-17", "Statement": []}
            for index in set:
                result_docs["Statement"].extend(policies[index]["Statement"])
            result_docs_list.append(result_docs)
        return result_docs_list

    # 정책 json 문서를 가지고 옴
    def get_policy_docs(self, policy_arn_list):
        serach_string = "arn:aws:iam::aws:policy/"  # aws 관리형 signature
        docs_list = []
        for policy_arn in policy_arn_list:
            _, policy_name = map(str, policy_arn.split("/"))
            if serach_string in policy_arn:
                collection = self.db["awsPolicies"]
                query_result = collection.find_one({"Arn": policy_arn})
                for index, statement in enumerate(
                    query_result["Document"]["Statement"]
                ):
                    statement["Sid"] = util.remove_special_characters(
                        f"{policy_name}{index+1}"
                    )
                docs_list.append(query_result["Document"])
            else:
                collection = self.db["awsCustomPolicies"]
                query_result = collection.find_one({"Arn": policy_arn})
                for index, statement in enumerate(
                    query_result["Document"]["Statement"]
                ):
                    statement["Sid"] = util.remove_special_characters(
                        f"{policy_name}{index+1}"
                    )
                docs_list.append(query_result["Document"])
        return docs_list

    # 직무를 aws iam 계정에 할당
    def position_sync_aws(self, aws_iam_user_name, position_name):
        new_policy_name = (f"boch-{position_name}-for-{aws_iam_user_name}").replace(
            " ", ""
        )
        query_result = self.positions_collection.find_one(
            {"positionName": position_name}
        )
        if query_result is None:
            raise HTTPException(status_code=500, detail="position not found")
        arn_list = [list(d.values())[0] for d in query_result["policies"]]
        docs_list = self.get_policy_docs(arn_list)
        docs_list = self.policy_compress(docs_list)
        new_policies = []
        index = 1
        for docs_index in range(len(docs_list)):
            if (type(docs_list[docs_index])) == int:
                new_policies.append(arn_list[docs_list[docs_index]])
                index -= 1
                continue
            else:
                policy_name = f"{new_policy_name}-{docs_index+index}"
                sdk_result = self.iam_sdk.create_policy(
                    PolicyName=policy_name,
                    PolicyDocument=json.dumps(docs_list[docs_index]),
                )
                new_policies.append(sdk_result["Policy"]["Arn"])

        for policy in new_policies:
            self.iam_sdk.attach_user_policy(
                UserName=aws_iam_user_name, PolicyArn=policy
            )

    def delete_old_position(self, aws_user_name, position_name):
        policies = self.positions_collection.find_one({"positionName": position_name})[
            "policies"
        ]
        arn_list = [list(d.values())[0] for d in policies]
        attached_policies = self.awsUsers_collection.find_one(
            {"UserName": aws_user_name}
        )["AttachedPolicies"]
        detach_policies = []
        for arn in arn_list:
            for policy in attached_policies:
                if policy["PolicyArn"] == arn:
                    detach_policies.append(arn)
                elif position_name.replace(" ", "") in policy["PolicyName"]:
                    detach_policies.append(policy["PolicyArn"])

        for policy_arn in detach_policies:
            try:
                self.iam_sdk.detach_user_policy(
                    UserName=aws_user_name, PolicyArn=policy_arn
                )
            except:
                pass

    # 유저를 생성했을 때 직무를 AWS에 적용하는 함수
    def user_create_sync(self, user_data):
        collection = self.db["awsUsers"]
        query_result = collection.find_one({"UserName": user_data.awsAccount})
        if query_result is None:
            raise HTTPException(status_code=500, detail="aws iam user not found")
        for postion_name in user_data.attachedPosition:
            self.position_sync_aws(user_data.awsAccount, postion_name)

    # 유저의 직무를 수정했을 때 직무를 적용하는 함수
    def user_update_sync(self, origin_user_data, new_user_data):
        aws_user_name = origin_user_data["awsAccount"]
        for postion_name in origin_user_data["attachedPosition"]:
            self.delete_old_position(aws_user_name, postion_name)
        for postion_name in new_user_data.attachedPosition:
            self.position_sync_aws(new_user_data.awsAccount, postion_name)

    def create_group(self, group_name):
        return self.aws_sdk.create_group(GroupName=group_name)

    def add_user_to_group(self, group_name, user_name):
        return self.aws_sdk.add_user_to_group(UserName=user_name, GroupName=group_name)

    def attach_group_policy(self, group_name, policy_arn):
        return self.aws_sdk.attach_group_policy(
            GroupName=group_name, PolicyArn=policy_arn
        )

    def attach_group_position(group_name, position_id):
        pass

    def update_awsUsers(user_name):
        pass

    def update_awsGroups(group_name):
        pass
