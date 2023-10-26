from pymongo import MongoClient

from database import db_client

from .aws_iam import awsSdk
from .config import conf


class awsIamSync:
    def __init__(self):
        self.client = MongoClient(conf["DB_server"], serverSelectionTimeoutMS=5000)
        self.db = self.client["Boch"]
        self.positions_collection = self.db["positions"]
        self.awsPolicies_collection = self.db["awsPolicies"]
        self.aws_sdk = awsSdk()
        pass

    def count_string(obj):
        string = str(obj)
        string = string.replace(" ", "")
        return len(string)

    def calculate_set(str_num):
        limit_string = 6000
        number_list = list(str_num)
        result = []
        while number_list:
            tmp = 0
            combine = []
            while number_list:
                if len(number_list) == 1:
                    combine.append(str_num.index(number_list.pop(0)))
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
                        number_list.pop(min_index)
                elif max_value + min_value > limit_string:
                    combine.append(str_num.index(max_value))
                    number_list.pop(max_index)
                    break
                else:
                    tmp = max_value + min_value
                    combine.append(str_num.index(max_value))
                    number_list.pop(max_index)
                    combine.append(str_num.index(min_value))
                    number_list.pop(number_list.index(min_value))
            result.append(combine)

        return result

    def get_policy_docs(self, policy_arn_list):
        serach_string = "arn:aws:iam::aws:policy"
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
        query_result = self.positions_collection.find_one(
            {"positionName": position_name}
        )
        docs_list = self.get_policy_docs(
            [[list(d.values())[0] for d in query_result["policies"]]]
        )

    def user_create_sync(self, user_data):
        collection = self.db["awsUsers"]
        query_result = collection.find_one({"UserName": user_data.awsAccount})
        if query_result is None:
            raise Exception("aws iam 계정이 없음")
        for postion_name in user_data.attachedPosition:
            self.position_sync_aws(user_data.awsAccount, postion_name)
        pass
