def get_boch_user_list(collection):
    try:
        result = list(collection.find())
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    return result


def get_boch_position_list(collection):
    try:
        result = list(collection.find())
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    return result


def get_boch_position_by_id(collection, position_id):
    try:
        result = collection.find_one({"_id": position_id})
    except Exception as e:
        return {"error": "server error", "detail": str(e)}

    if result is None:
        return {"result": "position not found"}

    return result


def delete_position_by_id(collection, position_id):
    try:
        position = collection.find_one({"_id": position_id})
    except Exception as e:
        return {"error": "server error", "detail": str(e)}
    
    if position:
        position_type = position.get("type")
        if position_type == "pre_define":
            return {"position_id": position_id, "result": "cannot delete pre-defined position"}
        else:
            result = collection.delete_one({"_id": position_id})
            if result.deleted_count == 1:
                return {"position_id": position_id, "result": "deleted successfully"}
            else:
                return {"position_id": position_id, "result": "deletion failed"}
    else:
        return {"position_id": position_id, "result": "position not found"}
