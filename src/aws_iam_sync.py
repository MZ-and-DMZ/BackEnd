import json

import boto3
from fastapi import HTTPException
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

    # 문자열의 문자 수를 반환해준다.
    def count_string(self, input):
        string = str(input)
        string = string.replace(" ", "")
        return len(string)

    # 정책을 합칠 수 있는 조합을 반환한다.
    def calculate_set(self, string_lengths):
        limit_string = 5000  # 최대 문자 수
        string_lengths_copy = string_lengths.copy()  # 입력받은 문자 수 리스트를 복사한다.
        string_lengths_copy.sort()  # 오름차 순으로 정렬
        result = []  # 결과를 저장할 리스트
        while len(string_lengths_copy) > 1:  # list안의 요소가 1개 이상일 경우 반복한다.
            index_set = []  # 찾아낸 조합을 저장할 리스트
            max_value = string_lengths_copy[-1]
            min_value = string_lengths_copy[0]
            max_value_index = string_lengths.index(
                string_lengths_copy.pop(-1)
            )  # 최댓값의 인덱스를 index_set 리스트에 추가하고 pop
            index_set.append(max_value_index)
            string_lengths[max_value_index] = -1  # 사용한 숫자를 재사용하지 못하게 -1로 변경
            total_value = max_value + min_value
            while total_value < limit_string:  # 최대 문자 수보다 작을 경우에만 반복
                min_value_index = string_lengths.index(
                    string_lengths_copy.pop(0)
                )  # 최솟값의 인덱스를 index_set에 추가하고 pop
                index_set.append(min_value_index)
                string_lengths[min_value_index] = -1
                if string_lengths_copy:  # 남은 값이 있을 경우 리스트의 최솟값을 다시 할당
                    min_value = string_lengths_copy[0]
                    total_value += min_value
                else:
                    break
            if len(index_set) > 1:
                result.append(index_set)
            else:
                result.extend(index_set)
        else:
            if string_lengths_copy:  # 반복문이 끝나고 값이 하나 있을 경우에 마지막 값의 index를 result에 추가
                result.append(string_lengths.index(string_lengths_copy[0]))

        return result

    # 정책을 합쳐준다.
    def policy_compress(self, policies):
        result_docs_list = []
        string_length = []
        for policy in policies:
            string_length.append(self.count_string(policy["Statement"]))
        index_set = self.calculate_set(string_length)
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

    # 유저를 생성했을 때 직무를 AWS에 적용하는 함수
    def user_create_sync(self, user_data):
        collection = self.db["awsUsers"]
        query_result = collection.find_one({"UserName": user_data.awsAccount})
        if query_result is None:
            raise HTTPException(status_code=500, detail="aws iam user not found")
        for postion_name in user_data.attachedPosition:
            self.position_sync_aws(user_data.awsAccount, postion_name)

    # 유저를 수정했을 때 직무를 적용하는 함수
    def user_update_sync(self, origin_user_data, new_user_data):
        pass
