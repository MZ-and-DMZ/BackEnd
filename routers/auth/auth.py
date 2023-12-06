from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models.schemas import auth
from src.database import mongodb
from src.login import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(path="/login")
async def login(user: auth):
    collection = mongodb.db["auth"]
    try:
        result = await collection.find_one({"_id": user.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result is None:
        raise HTTPException(status_code=404, detail="user not found")

    password = result.get("password")

    if password is not None and isinstance(password, str):
        password = password.encode("utf-8")

    if verify_password(user.password, password):
        return JSONResponse(content={"message": "login success"}, status_code=200)

    return JSONResponse(content={"message": "password is incorrect"}, status_code=401)
