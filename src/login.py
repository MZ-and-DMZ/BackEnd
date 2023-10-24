from .password_hash import verify_password
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def auth_user(user, collection):
    try:
        result = collection.find_one({"_id": user.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result is None:
        raise HTTPException(status_code=404, detail="user not found")

    hashed_password = result.get("password")

    if hashed_password is not None and isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    if verify_password(user.password, hashed_password):
        return JSONResponse(content={"message": "login success"}, status_code=200)

    return JSONResponse(content={"message": "password is incorrect"}, status_code=401)
