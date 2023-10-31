import requests
from fastapi.responses import JSONResponse


# 주어진 url에서 파일 크기를 가져오는 함수
def get_file_size(url):
    response = requests.head(url)
    if 'content-length' in response.headers:
        return int(response.headers['content-length'])
    return None

def download_and_update_actions(size_collection, collection):
    github_url = "https://raw.githubusercontent.com/TryTryAgain/aws-iam-actions-list/master/all-actions.txt"
    current_file_size = get_file_size(github_url)  # 현재 파일 크기 가져오기

    size_result = size_collection.find_one({"fileName": github_url})

    if size_result is not None:
        previous_file_size = size_result.get("fileSize")
    else:
        previous_file_size = None

    if current_file_size != previous_file_size:
        collection.delete_many({})
        response = requests.get(github_url)
        if response.status_code == 200:
            actions = response.text.split("\n")
            service_action_dict = {}

            for action in actions:
                parts = action.strip().split(":")
                if len(parts) == 2:
                    service, action_name = parts
                    if service not in service_action_dict:
                        service_action_dict[service] = []
                    service_action_dict[service].append(f"{service}:{action_name}")

            for service, action_list in service_action_dict.items():
                document = {
                    "serviceName": service,
                    "actionList": action_list
                }
                collection.insert_one(document)

            if size_result is not None:
                size_collection.update_one({"fileName": github_url}, {"$set": {"fileSize": current_file_size}})
            else:
                size_collection.insert_one({"fileName": github_url, "fileSize": current_file_size})

            return JSONResponse(content={"message": "actions updated successfully"}, status_code=200)
    else:
        return JSONResponse(content={"message": "update is not needed"}, status_code=200)

