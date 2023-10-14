def get_boch_user_list(collection):
    try:
        result = list(collection.find())
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    return {"user_list": result}


def get_boch_user(collection, user_id):
    try:
        result = collection.find_one({"_id": user_id})
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    if result is None:
        return {"result": "user not found"}

    return result


def create_boch_user(collection, user_data):
    new_user = {
        "_id": user_data.user_id,
        "description": user_data.description,
        "aws_account": user_data.aws_account,
        "gcp_account": user_data.gcp_account,
        "attached_position": user_data.attached_position,
        "attached_group": user_data.attached_group,
        "updatetime": user_data.updatetime,
    }

    try:
        result = collection.insert_one(new_user)
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    if result.acknowledged:
        return {"result": f"{user_data.user_id} created successfully"}
    else:
        return {"result": "failed to create position"}


def update_boch_user(collection, user_data):
    pass


def delete_boch_user(collection, user_id_list):
    result = dict()  # 삭제 결과 JSON
    for user_id in user_id_list:
        try:  # 삭제하기 전 DB에 있는지 검색
            user = collection.find_one({"_id": user_id})
            if user is None:
                result[user_id] = "position not found"
                continue
        except Exception as e:
            return {"error": "server error", "detail": str(e)}

        delete_result = collection.delete_one({"_id": user_id})  # 삭제
        if delete_result.deleted_count == 1:
            result[user_id] = "deleted successfully"
        else:
            result[user_id] = "deletion failed"

    return result


def get_boch_position_list(collection):
    try:
        result = list(collection.find())
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    return {"position_list": result}


def get_boch_position(collection, position_id):
    try:
        result = collection.find_one({"_id": position_id})
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    if result is None:
        return {"result": "position not found"}

    return result


def delete_position(collection, position_id_list):
    result = dict()
    for position_id in position_id_list:
        try:
            position = collection.find_one({"_id": position_id})
        except Exception as e:
            return {"error": "server error", "detail": str(e)}

        if position["type"] == "pre_define":
            result[position_id] = "cannot delete pre-defined position"
        elif position["type"] == "custom":
            delete_result = collection.delete_one({"_id": position_id})
            if delete_result.deleted_count == 1:
                result[position_id] = "deleted successfully"
            else:
                result[position_id] = "deletion failed"
        else:
            result[position_id] = "position not found"

    return result
