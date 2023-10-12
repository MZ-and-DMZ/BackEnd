from .password_hash import verify_password


def auth_user(user, collection):
    try:
        result = collection.find_one({"_id": user.id})
    except Exception as e:
        return {"result": "server error", "detail": str(e)}

    if result is None:
        return {"result": "user not exist"}

    hashed_password = result.get("password")

    if hashed_password is not None and isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    if verify_password(user.pwd, hashed_password):
        return {"result": "success"}

    return {"result": "password is incorrect"}
