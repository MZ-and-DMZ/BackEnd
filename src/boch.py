def get_boch_user_list(collection):
    try:
        result = list(collection.find())
    except:
        return "server error"
    return result
