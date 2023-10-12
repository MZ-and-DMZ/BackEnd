def get_boch_user_list(collection):
    try:
        result = list(collection.find())
    except:
        return "server error"
    return result


def get_boch_user(collection):
    try:
        result = collection.findOne()
    except:
        pass
