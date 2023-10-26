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
        pass

    def count_string(self, obj):
        string = str(obj)
        string = string.replace(" ", "")
        return len(string)

    def calculate_set(self, str_num):
        limit_string = 5000
        number_list = list(str_num)
        result = []
        while number_list:
            tmp = 0
            combine = []
            while number_list:
                if len(number_list) == 1:
                    combine.append(str_num.index(number_list.pop(0)))
                    str_num[combine[-1]] = 0
                    break
                max_value = max(number_list)
                max_index = number_list.index(max_value)
                min_value = min(number_list)
                min_index = number_list.index(min_value)
                if tmp != 0:
                    if tmp + min_value > limit_string:
                        break
                    else:
                        tmp = tmp + min_value
                        combine.append(str_num.index(min_value))
                        str_num[combine[-1]] = 0
                        number_list.pop(min_index)
                elif max_value + min_value > limit_string:
                    combine.append(str_num.index(max_value))
                    str_num[combine[-1]] = 0
                    number_list.pop(max_index)
                    break
                else:
                    tmp = max_value + min_value
                    combine.append(str_num.index(max_value))
                    str_num[combine[-1]] = 0
                    number_list.pop(max_index)
                    combine.append(str_num.index(min_value))
                    str_num[combine[-1]] = 0
                    number_list.pop(number_list.index(min_value))
            result.append(combine)

        return result

    def policy_compress(self, policies):
        result_docs_list = []
        str_num = []
        for policy in policies:
            str_num.append(self.count_string(policy["Statement"]))
        index_set = self.calculate_set(str_num)
        for set in index_set:
            if len(set) == 1:
                result_docs_list.append(set[0])
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
        pass
