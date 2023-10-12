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
