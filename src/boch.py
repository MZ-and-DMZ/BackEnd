def get_boch_user_list(collection):
    try:
        result = list(collection.find())
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    return {"user_list": result}


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


# 직무 생성하기
def create_position(position, collection):
    # 직무 이름을 입력하지 않을 경우
    if not position.position_name.strip():
        return {"result": "position name is required"}

    # 직무 타입이 custom이 아닌 경우
    if position.type != "custom":
        return {"result": "position type must be 'custom'"}

    new_position = {
        "_id": position.position_name,
        "type": position.type,
        "description": position.description,
        "aws_policies": position.aws_policies,
        "gcp_policies": position.gcp_policies
    }

    try:
        result = collection.insert_one(new_position)
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    if result.acknowledged:
        return {"result": f"{str(result.inserted_id)} created successfully"}
    else:
        return {"result": "failed to create position"}


# 직무 수정하기
def update_position(position_id, position, collection):
    existing_position = collection.find_one({"_id": position_id})

    if existing_position is None:
        return {"result": "position not found"}

    update_query = {
        "$set": {
            "_id": position.position_name,
            "type": position.type,
            "description": position.description,
            "aws_policies": position.aws_policies,
            "gcp_policies": position.gcp_policies
        }
    }

    try:
        result = collection.update_one({"_id": position_id}, update_query)
    except Exception as e:
        return {"error": "Server error", "detail": str(e)}

    if result.modified_count > 0:
        return {"result": f"{position_id} updated successfully"}
    else:
        return {"result": f"no modifications for {position_id}"}


# 직무 삭제하기
def delete_position(collection, position_id_list):
    result = dict()
    for position_id in position_id_list:
        try:
            position = collection.find_one({"_id": position_id})

            if position is None:
                result[position_id] = "position not found"
                continue
        except Exception as e:
            return {"error": "server error", "detail": str(e)}

        # 직무 타입이 pre-define일 경우
        if position["type"] == "pre_define":
            result[position_id] = "cannot delete pre-defined position"
        else:
            delete_result = collection.delete_one({"_id": position_id})
            if delete_result.deleted_count == 1:
                result[position_id] = "deleted successfully"
            else:
                result[position_id] = "deletion failed"

    return result
