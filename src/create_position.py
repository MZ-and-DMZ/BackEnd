import json
from typing import List

from src import util
from src.database import mongodb

from .boto3_connect import aws_sdk


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
    aws_sdk.iam_connect()
    arns = []
    for policy in policies:
        arns.extend(list(policy.values()))
    docs_list = await get_policy_docs(arns)
    docs_list = await policy_compress(docs_list)
    position_arns = []
    policy_num = 1
    for index, docs in enumerate(docs_list):
        if isinstance(docs, int):
            position_arns.append(arns[docs])
            policy_num -= 1
        else:
            sdk_result = aws_sdk.client.create_policy(
                PolicyName=f"{position_name}-{index+policy_num}",
                PolicyDocument=json.dumps(docs),
            )
            position_arns.append(sdk_result["Policy"]["Arn"])
    else:
        aws_sdk.iam_close()
    collection = mongodb.db["positionLink"]
    schema = {"_id": position_name, "arns": position_arns}
    insert_result = await collection.insert_one(schema)
