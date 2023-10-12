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
