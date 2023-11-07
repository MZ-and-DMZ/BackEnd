import json
import re

from bson import json_util


def bson_to_json(data):
    return json.loads(json_util.dumps(data))


# 문자열 특수문자 제거 후 반환
def remove_special_characters(string):
    return re.sub(r"[^A-Za-z0-9\s]", "", string)


# 들어온 변수를 string으로 바꾸고 string의 문자 수를 반환
def count_string(input):
    string = str(input)
    string = string.replace(" ", "")
    return len(string)


# 최대로 합칠 수 있는 숫자의 조합을 반환한다.
def calculate_set(int_list):
    limit_string = 5000  # 최대 문자 수
    int_list_copy = int_list.copy()  # 입력받은 문자 수 리스트를 복사한다.
    int_list_copy.sort()  # 오름차 순으로 정렬
    result = []  # 결과를 저장할 리스트
    while len(int_list_copy) > 1:  # list안의 요소가 1개 이상일 경우 반복한다.
        index_set = []  # 찾아낸 조합을 저장할 리스트
        max_value = int_list_copy[-1]
        min_value = int_list_copy[0]
        max_value_index = int_list.index(
            int_list_copy.pop(-1)
        )  # 최댓값의 인덱스를 index_set 리스트에 추가하고 pop
        index_set.append(max_value_index)
        int_list[max_value_index] = -1  # 사용한 숫자를 재사용하지 못하게 -1로 변경
        total_value = max_value + min_value
        while total_value < limit_string:  # 최대 문자 수보다 작을 경우에만 반복
            min_value_index = int_list.index(
                int_list_copy.pop(0)
            )  # 최솟값의 인덱스를 index_set에 추가하고 pop
            index_set.append(min_value_index)
            int_list[min_value_index] = -1
            if int_list_copy:  # 남은 값이 있을 경우 리스트의 최솟값을 다시 할당
                min_value = int_list_copy[0]
                total_value += min_value
            else:
                break
        if len(index_set) > 1:
            result.append(index_set)
        else:
            result.extend(index_set)
    else:
        if int_list_copy:  # 반복문이 끝나고 값이 하나 있을 경우에 마지막 값의 index를 result에 추가
            result.append(int_list.index(int_list_copy[0]))

    return result
