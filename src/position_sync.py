from typing import List

from models import mongodb
from src import util

# from .boto3_connect import iam_client


async def get_policy_docs(arns: List[str]):
    collection = mongodb.db["awsPolicyDocs"]
    docs_list = []

    for arn in arns:
        _, policy_name = map(str, arn.split("/"))
        find_result = await collection.find_one({"_id": arn})
        for index, statement in enumerate(find_result["Document"]["Statement"]):
            statement["Sid"] = util.remove_special_characters(f"{policy_name}{index+1}")
        docs_list.append(find_result["Document"])

    return docs_list


async def policy_compress(docs_list):
    result_docs_list = []
    string_length = []
    for docs in docs_list:
        string_length.append(util.count_string(docs["Statement"]))
    index_set = util.calculate_set(string_length)
    for set in index_set:
        if isinstance(set, int):
            result_docs_list.append(set)
            continue
        result_docs = {"Version": "2012-10-17", "Statement": []}
        for index in set:
            result_docs["Statement"].extend(docs_list[index]["Statement"])
        result_docs_list.append(result_docs)
    return result_docs_list


async def create_position_aws(position_name: str, policies: List[dict]):
    arns = []
    for policy in policies:
        arns.extend(list(policy.values()))
    docs_list = await get_policy_docs(arns)
    docs_list = await policy_compress(docs_list)

    print(docs_list)
    # for index, docs in enumerate(docs_list):
