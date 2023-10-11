def auth_user(user, collection):
    result = collection.find_one({"_id": user.id})

    if result:
        if result.get("password") == user.pwd:
            return {"result": "success"}
        else:
            return {"result": "password is incorrect"}
    else:
        return {"result": "user not exist"}
