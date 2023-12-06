import re
from itertools import combinations

from src.database import mongodb


async def check(pattern, action):
    action_asterisk = "none"
    # *가 포함된 경우
    match = re.match(pattern, action)
    if match:
        # * 앞에 있는 문자열 추출
        action_asterisk = match.group(1)
    return action_asterisk


# AWS 전체 권한 가져오기
async def get_aws_managed_policies():
    collection = mongodb.db["awsPolicyAction"]
    awsPermissionDict = {}
    result = await collection.find().to_list(None)

    for document in result:
        Allow = document.get("Allow", [])
        Deny = document.get("Deny", [])
        awsPermissionDict[document["_id"]] = {
            "Allow": set(Allow) if Allow else set(),
            "Deny": set(Deny) if Deny else set(),
            "count": document.get("count"),
        }

    return awsPermissionDict


# 정책명으로 개수 가져오기
async def get_count_policyName(policy_name):
    collection = mongodb.db["awsPolicyAction"]
    # AmazonZocaloFullAccess, AmazonZocaloReadOnlyAccess은 정책에 저장되지 않았음.
    result = await collection.find({"_id": policy_name}, {"count": 1}).to_list(None)
    # Cursor에서 값을 가져와 반환
    count = result[0].get("count", 0) if result else 0

    return count


# 정책 추천하거나 none 반환 - 선택한 권한이 포함된 정책 딕셔너리 전달
async def recommend_or_none(action_dict):
    # 최소 권한 개수에 해당하는 정책 한 개 추천
    recommend_policy_name = min(action_dict, key=action_dict.get, default=None)
    return recommend_policy_name


# 넘어오는 권한 목록으로 조합 생성
async def aws_combination(policy_dict, selected_action_set):
    # 조합된 정책의 권한이 합쳐져 저장될 딕셔너리
    contain_combinations_dict = {}

    # 정책명들이 key에 리스트로 저장됨
    keys = list(policy_dict.keys())

    # 조합 시 nCm이라면 m은 1부터 시작. 전체 조합까지도 갈 수 있음.
    for m in range(1, len(keys) + 1):
        for combination in combinations(keys, m):
            combined_set = set()
            for key in combination:
                combined_set.update(policy_dict[key]["action"])

            if selected_action_set.issubset(combined_set):
                count = 0
                for key in combination:
                    count += policy_dict[key]["count"]
                contain_combinations_dict[combination] = count
    # 모든 조합 생성하고 반환
    return contain_combinations_dict


# 정책과 선택한 권한의 교집합 찾기
async def get_intersect_action(policy_dict, selected_action_set):
    # 선택한 권한이랑 겹치는 권한을 딕셔너리에 저장
    intersection_dict = {}

    for aws_policy_name, json in policy_dict.items():
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
                    intersection_dict[aws_policy_name] = {
                        "action": intersection_set,
                        "count": json["count"],
                    }
            # 관리형 정책에 *이 포함된 경우
            else:
                # allow_asterisk_set의 권한이 선택한 권한을 포함하는지 확인 - 문자열 일부에 포함되는 경우 있다고 set에 추가
                for asterisck_action in allow_asterisk_set:
                    for selected_action in selected_action_set:
                        if selected_action.startswith(asterisck_action):
                            contain_action_set.add(selected_action)

                if contain_action_set:
                    # 교집합 저장
                    intersection_dict[aws_policy_name] = {
                        "action": selected_action_set.intersection(contain_action_set),
                        "count": json["count"],
                    }

    return intersection_dict


async def aws_min_intersect_permission(intersect_dict):
    # 교집합한 권한이 같은지 확인
    # {frozenset({'권한'}): ['정책', ,,]} 형식으로 저장됨
    policy_with_same_values = {}

    for key, value in intersect_dict.items():
        action_set = frozenset(value["action"])
        policy_with_same_values.setdefault(action_set, []).append(
            {"policy": key, "count": value["count"]}
        )

    min_intersection_dict = {}

    for value_set, roles in policy_with_same_values.items():
        min_role = min(roles, key=lambda x: (x["count"]))

        min_intersection_dict[min_role["policy"]] = {
            "action": value_set,
            "count": min_role["count"],
        }

    return min_intersection_dict


async def find_best_awsPolicy(selected_action_set):
    aws_policy_dict = await get_aws_managed_policies()

    intersect_dict = await get_intersect_action(aws_policy_dict, selected_action_set)
    min_intersect_dict = await aws_min_intersect_permission(intersect_dict)
    combi_result = await aws_combination(min_intersect_dict, selected_action_set)
    recommend_name = await recommend_or_none(combi_result)

    return list(recommend_name)


# gcp 역할 : 권한 목록 딕셔너리 반환
async def get_gcp_RolePermission():
    # {”역할명” : [”권한명”,””],~~} 형태로 저장
    gcpRoleDict = {}

    collection = mongodb.db["gcpRoleDocs"]
    result = await collection.find(
        {}, {"_id": 1, "includedPermissions": 1, "permissionCount": 1}
    ).to_list(None)

    for document in result:
        permissions = document.get("includedPermissions", [])
        gcpRoleDict[document["_id"]] = {
            "permission": set(permissions) if permissions else set(),
            "count": document.get("permissionCount"),
        }

    return gcpRoleDict


# 교집합 권한 딕셔너리 반환
async def get_intersect_permission(gcp_permission, selected_permission):
    intersection_dict = {}

    for role_name, permission_set in gcp_permission.items():
        intersection_set = selected_permission.intersection(
            permission_set["permission"]
        )

        if intersection_set:
            intersection_dict[role_name] = {
                "permission": intersection_set,
                "count": permission_set["count"],
            }

    return intersection_dict


# 중복되는 교집합 권한 세트 있으면 역할명 하나만 남기고 제거
async def gcp_min_intersect_permission(intersect_dict):
    # 교집합 권한 세트 딕셔너리
    role_with_same_values = {}

    for key, value in intersect_dict.items():
        permission_set = frozenset(value["permission"])
        role_with_same_values.setdefault(permission_set, []).append(
            {"role": key, "count": value["count"]}
        )

    # 교집합 세트가 중복되는 경우 {개수가 가장 작은 역할명 : {교집합 권한, 개수}}의 형태로 딕셔너리에 저장
    min_intersection_dict = {}

    for value_set, roles in role_with_same_values.items():
        min_role = min(roles, key=lambda x: (x["count"]))

        min_intersection_dict[min_role["role"]] = {
            "permission": value_set,
            "count": min_role["count"],
        }

    return min_intersection_dict


# 모든 조합 생성
async def gcp_combination(intersect_dict, selected_permission_set):
    # 조합된 정책의 권한이 합쳐져 저장될 딕셔너리
    contain_combinations_dict = {}

    # 정책명들이 key에 리스트로 저장됨
    keys = list(intersect_dict.keys())

    # 조합 시 nCm이라면 전체 조합까지 실행
    for m in range(1, len(keys) + 1):
        for combination in combinations(keys, m):
            combined_set = set()
            for key in combination:
                combined_set.update(intersect_dict[key]["permission"])

            if selected_permission_set.issubset(combined_set):
                count = 0
                for key in combination:
                    count += intersect_dict[key]["count"]
                contain_combinations_dict[combination] = count
    # {(역할 조합): 개수, ..}의 형식
    return contain_combinations_dict


async def recommend_or_none(contain_dict):
    recommend_policy_name = min(contain_dict, key=contain_dict.get, default=None)
    return recommend_policy_name


async def find_best_gcpRole(selected_permission_set):
    # 역할 권한 가져오기
    gcpRoleDict = await get_gcp_RolePermission()

    # 선택한 권한과 관리형 정책의 교집합 세트
    intersect_dict = await get_intersect_permission(
        gcpRoleDict, selected_permission_set
    )
    # 교집합 권한 세트가 같은 역할명 중 권한 개수 가장 작은 역할명만 남겨서 딕셔너리에 저장
    min_intersect_dict = await gcp_min_intersect_permission(intersect_dict)
    # 조합 생성
    combi_result = await gcp_combination(min_intersect_dict, selected_permission_set)
    # 개수가 가장 작은 하나의 조합만 반환
    recommend_name = await recommend_or_none(combi_result)

    return list(recommend_name)
