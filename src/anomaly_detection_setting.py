from datetime import datetime

# 시간 형식 변환 함수
def str_to_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

# 시간 형식을 문자열로 변환 함수
def time_to_str(time_obj):
    return time_obj.strftime("%H:%M")