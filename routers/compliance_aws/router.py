from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json
import src.aws_compliance as aws_compliance

router = APIRouter(prefix="/compliance/aws", tags=["compliance aws"])


@router.get(path="/check/list")
async def aws_check_list():
    collection = mongodb.db["awsComplianceList"]
    try:
        check_list = await collection.find({}).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"aws_check_list": bson_to_json(check_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/check/root/access/key/active")
async def check_root_key_from_credential_report():
    try:
        result = await aws_compliance.check_root_key_from_credential_report()
        res_json = bson_to_json({
            "result": result
        })
        return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/check/root/account/usage")
async def check_root_account_usage():
    try:
        account_id = await aws_compliance.get_account_id()
        result = await aws_compliance.check_root_account_usage(account_id)
        res_json = bson_to_json({
            "result": result
        })
        return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/check/user/access/key/date")
async def check_user_access_key_date():
    try:
        all_user_key_diff = await aws_compliance.check_user_access_key_date()
        res_json = bson_to_json({
            "result": all_user_key_diff
        })
        return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/update/access/key")
async def update_access_key(duration: int):
    try:
        await aws_compliance.update_access_key(duration)
        return {"message": "successfully updated access key"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/set/password/policy")
async def password_policy():
    try:
        await aws_compliance.password_policy(length=8, MaxAge=90)
        return {"message": "successfully set password policy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))