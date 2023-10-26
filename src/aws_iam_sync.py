import json

import boto3
from pymongo import MongoClient

from database import db_client

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

    def count_string(self, input):
        string = str(input)
        string = string.replace(" ", "")
        return len(string)

    def calculate_set(self, string_lengths):
        limit_string = 5000
        string_lengths_copy = string_lengths.copy()
        string_lengths_copy.sort()
        result = []

        while len(string_lengths_copy) > 1:
            index_set = []
            max_value = string_lengths_copy[-1]
            min_value = string_lengths_copy[0]
            max_value_index = string_lengths.index(string_lengths_copy.pop(-1))
            index_set.append(max_value_index)
            string_lengths[max_value_index] = -1
            total_value = max_value + min_value
            while total_value < limit_string:
                min_value_index = string_lengths.index(string_lengths_copy.pop(0))
                index_set.append(min_value_index)
                string_lengths[min_value_index] = -1
                if string_lengths_copy:
                    min_value = string_lengths_copy[0]
                    total_value += min_value
                else:
                    break
            if len(index_set) > 1:
                result.append(index_set)
            else:
                result.extend(index_set)
        else:
            if string_lengths_copy:
                result.append(string_lengths.index(string_lengths_copy[0]))

        return result

    def policy_compress(self, policies):
        result_docs_list = []
        str_num = []
        for policy in policies:
            str_num.append(self.count_string(policy["Statement"]))
        index_set = self.calculate_set(str_num)
        for set in index_set:
            if isinstance(set, int):
                result_docs_list.append(set)
                continue
            result_docs = {"Version": "2012-10-17", "Statement": []}
            for index in set:
                result_docs["Statement"].extend(policies[index]["Statement"])
            result_docs_list.append(result_docs)
        return result_docs_list

    def get_policy_docs(self, policy_arn_list):
        serach_string = "arn:aws:iam::aws:policy/"
        docs_list = []
        for policy_arn in policy_arn_list:
            if serach_string in policy_arn:
                collection = self.db["awsPolicies"]
                query_result = collection.find_one({"Arn": policy_arn})
                docs_list.append(query_result["Document"])
            else:
                collection = self.db["awsCustomPolicies"]
                query_result = collection.find_one({"Arn": policy_arn})
                docs_list.append(query_result["Document"])
        return docs_list

    # 직무를 aws iam 계정에 할당
    def position_sync_aws(self, aws_iam_user_name, position_name):
        new_policy_name = f"boch-policy-for-{aws_iam_user_name}"
        query_result = self.positions_collection.find_one(
            {"positionName": position_name}
        )
        arn_list = [list(d.values())[0] for d in query_result["policies"]]
        docs_list = self.get_policy_docs(arn_list)
        docs_list = self.policy_compress(docs_list)

        new_policies = []
        index = 0
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

    def user_create_sync(self, user_data):
        collection = self.db["awsUsers"]
        query_result = collection.find_one({"UserName": user_data.awsAccount})
        if query_result is None:
            raise Exception("aws iam 계정이 없음")
        for postion_name in user_data.attachedPosition:
            self.position_sync_aws(user_data.awsAccount, postion_name)
