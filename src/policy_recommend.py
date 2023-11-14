import re
from itertools import combinations

from models import mongodb


async def check(pattern, action):
    action_asterisk = "none"
    # *가 포함된 경우
    match = re.match(pattern, action)
    if match:
        # * 앞에 있는 문자열 추출
        action_asterisk = match.group(1)
        # print("매치됨")
    return action_asterisk


# 정책명으로 개수 가져오기
async def get_count_policyName(policy_name):
    collection = mongodb.db["awsPolicyAction"]
    result = await collection.find_one({"_id": policy_name}, {"count": 1})
    count = result.get("count", 0) if result else 0

    return count


# 정책 추천하거나 none 반환 - 선택한 권한이 포함된 정책 딕셔너리 전달
async def recommend_or_none(action_dict):
    if len(action_dict) == 0:
        recommend_policy_name = None
        # 부분 + 부분을 할 방법을 고안해보기

    # 하나의 권한에 선택한 권한이 모두 포함되는 경우
    else:
        # 권한 추천 후보 확인
        print("후보 개수 : ", len(action_dict))
        # print(action_dict)
        # 최소 권한 개수에 해당하는 정책 한 개 추천
        recommend_policy_name = min(action_dict, key=action_dict.get)
        print("추천 정책명 : ", recommend_policy_name)

    return recommend_policy_name


# 넘어오는 권한 목록으로 조합 생성
async def combination(policy_dict, selected_action_set):
    # 조합된 정책의 권한이 합쳐져 저장될 딕셔너리
    contain_combinations_dict = {}

    result = False

    # 정책명들이 key에 리스트로 저장됨
    keys = list(policy_dict.keys())

    # 조합 시 nCm이라면 m은 2부터 시작. 전체 조합까지도 갈 수 있음.
    for m in range(2, len(keys) + 1):
        for combination in combinations(keys, m):
            combined_set = set()
            for key in combination:
                combined_set.update(policy_dict[key])

            if selected_action_set.issubset(combined_set):
                count = 0
                for key in combination:
                    count += await get_count_policyName(key)
                contain_combinations_dict[combination] = count
        # m 번의 조합으로 선택한 전체 권한이 커버되는 경우 조합 생성 멈추기
        result = await recommend_or_none(contain_combinations_dict)
        if result:
            break
    # result = recommend_or_none(contain_combinations_dict)
    return result


# 교집합이 선택한 권한에 포함되는지 확인
async def check_if_subset(intersect_dict, selected_action_set):
    # 조합된 정책의 권한이 합쳐져 저장될 딕셔너리
    contain_combinations_dict = {}

    for policy_name, intersect_action in intersect_dict.items():
        # 선택한 권한이 조합한 권한 세트에 포함되는 경우
        is_subset = selected_action_set.issubset(intersect_action)
        if is_subset:
            # 두 정책의 권한 개수 더해서 {"정책명":개수}의 형태로 딕셔너리에 저장
            contain_combinations_dict[policy_name] = await get_count_policyName(
                policy_name
            )

    result = await recommend_or_none(contain_combinations_dict)
    return result


# 정책과 선택한 권한의 교집합 찾기
async def get_intersect_action(policy_dict, selected_action_set):
    # 선택한 권한이랑 겹치는 권한을 딕셔너리에 저장
    intersection_dict = {}

    for aws_policy_name, json in policy_dict.items():
        if "AdministratorAccess" in aws_policy_name:
            continue
        # 정책에 Deny가 있는 경우
        if "Deny" in json:
            aws_deny_set = set(json["Deny"])
            # A와 B 세트 간의 교집합을 찾음
            intersection_set = selected_action_set.intersection(aws_deny_set)

            # 교집합이 비어있지 않다면 넘어감 - 선택한 권한이 deny에 포함되어 있음
            if intersection_set:
                continue

            # *이 포함된 정책인지 확인하기 위한 변수
            deny_asterisk = False
            for action in aws_deny_set:
                action_asterisk_deny = await check(r"^(.*)(\*+)$", action)
                # 모든 서비스의 모든 권한인 경우는 제외됨. ""이 전달되기 때문에
                # 선택한 권한이 *가 포함된 deny에 해당하는지 여부 확인
                deny_action_contained = False
                if action_asterisk_deny != "none":
                    for selected_action in selected_action_set:
                        if selected_action.startswith(action_asterisk_deny):
                            deny_action_contained = True
                            break
                if deny_action_contained:
                    deny_asterisk = True
                    break
            if deny_asterisk:
                continue

        if "Allow" in json:
            # allow 처리
            aws_allow_set = set(json["Allow"])
            # * 를 제거한 세트를 새로 생성
            allow_asterisk_set = set()
            # *로 처리된 정책들과 선택한 권한을 비교하였을 때 *에 포함되는 권한인 경우 선택한 권한이 set에 추가됨
            contain_action_set = set()

            # *이 포함된 정책인지 확인하기 위한 변수
            asterisk = False
            for action in aws_allow_set:
                action_asterisk = await check(r"^(.*)(\*+)$", action)
                # print(type(action_asterisk))
                # if action_asterisk != "none":
                # 모든 서비스의 모든 권한인 경우는 제외됨. ""이 전달되기 때문에
                if action_asterisk != "none":
                    asterisk = True
                    allow_asterisk_set.add(action_asterisk)
                # *이 없는 경우는 그냥 추가하기
                else:
                    allow_asterisk_set.add(action)

            # 관리형 정책에 *이 포함되어 있지 않은 경우
            if asterisk == False:
                # 교집합이 있는지 확인
                intersection_set = selected_action_set.intersection(aws_allow_set)
                if intersection_set:
                    # 교집합을 저장함
                    intersection_dict[aws_policy_name] = intersection_set
            # 관리형 정책에 *이 포함된 경우
            else:
                # allow_asterisk_set의 권한이 선택한 권한을 포함하는지 확인 - 문자열 일부에 포함되는 경우 있다고 set에 추가
                for asterisck_action in allow_asterisk_set:
                    for selected_action in selected_action_set:
                        if selected_action.startswith(asterisck_action):
                            contain_action_set.add(selected_action)

                if contain_action_set:
                    # 교집합 저장
                    intersection_dict[
                        aws_policy_name
                    ] = selected_action_set.intersection(contain_action_set)

    # print(intersection_dict)
    return intersection_dict


async def get_aws_managed_policies():
    collection = mongodb.db["awsPolicies"]
    pipeline = [
        {
            "$lookup": {
                "from": "awsPolicyDocs",  # 조인할 컬렉션 이름
                "localField": "_id",  # 현재 컬렉션의 필드
                "foreignField": "_id",  # 조인할 컬렉션의 필드
                "as": "policy_docs",  # 결과를 저장할 필드 이름
            }
        },
        {"$project": {"_id": 1, "PolicyName": 1, "policy_docs.Document": 1}},
    ]
    policies_list = [doc async for doc in collection.aggregate(pipeline)]
    policy_dict = {}
    for policy in policies_list:
        policy_dict[policy["PolicyName"]] = {}
        policy_statements = policy["policy_docs"][0]["Document"]["Statement"]

        if type(policy_statements) == dict:
            policy_statements = [policy_statements]

        # allow_set = set()
        # deny_set = set()
        allow_list, deny_list = [], []

        for statement in policy_statements:
            if "Action" in statement:
                action = statement["Action"]
                if statement["Effect"] == "Allow":
                    if type(action) == list:
                        # action 세트를 추가
                        allow_list.extend(statement["Action"])
                    else:
                        allow_list.extend([statement["Action"]])
                    policy_dict[policy["PolicyName"]]["Allow"] = allow_list
                elif statement["Effect"] == "Deny":
                    if type(action) == list:
                        deny_list.extend(statement["Action"])
                    else:
                        deny_list.extend([statement["Action"]])
                    policy_dict[policy["PolicyName"]]["Deny"] = deny_list
            elif "NotAction" in statement:
                # print(policy['PolicyName'])
                action = statement["NotAction"]
                # print(action)
                if statement["Effect"] == "Allow":
                    if type(action) == list:
                        action = set(statement["NotAction"])
                    else:
                        action = set([statement["NotAction"]])
                    policy_dict[policy["PolicyName"]]["Allow"] = action
                # Deny NotAction이면 허용에 넣어줌
                elif statement["Effect"] == "Deny":
                    if type(action) == list:
                        allow_list.extend(statement["NotAction"])
                    else:
                        allow_list.extend([statement["NotAction"]])
                    policy_dict[policy["PolicyName"]]["Allow"] = allow_list
        # put_actionlist_DB(client, policy['PolicyName'], allow_list, deny_list)
    return policy_dict


async def find_best_awsPolicy(selected_action_set):
    intersect_dict = {}
    aws_policies = await get_aws_managed_policies()
    # 선택한 권한과 관리형 정책의 교집합 세트
    intersect_dict = await get_intersect_action(aws_policies, selected_action_set)
    isContainedOne = await check_if_subset(intersect_dict, selected_action_set)

    # 한 개의 정책에 포함되는 경우
    if isContainedOne:
        pass
    # 정책 조합이 필요한 경우
    else:
        # 교집합을 조합해서 {('정책명','정책명' -- ) : 개수}를 반환
        combi_result = await combination(intersect_dict, selected_action_set)
        if combi_result:
            return combi_result
        else:
            # 뭔가 이상한거
            print("정책 추천 불가")
