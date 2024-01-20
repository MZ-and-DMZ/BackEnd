from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json
from src.gcp_compliance import gcp_credentials, gcp_project_id
import src.gcp_compliance as gcp_compliance

router = APIRouter(prefix="/compliance/gcp", tags=["compliance gcp"])


@router.get(path="/check/list")
async def gcp_check_list():
    collection = mongodb.db["gcpComplianceList"]
    try:
        check_list = await collection.find({}).to_list(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"gcp_check_list": bson_to_json(check_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.get(path="/get/admin/account/logs")
async def get_admin_account_logs(admin_email: str, days_threshold: int):
    try:
        result, inserted_id = await gcp_compliance.get_admin_account_logs(gcp_credentials, gcp_project_id, admin_email, days_threshold)
        res_json = bson_to_json({
            "result": result,
            "inserted_id": inserted_id
        })
        return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post(path="/save/admin/account/logs")
async def save_mongodb_to_csv(insert_id: str):
    try:
        await gcp_compliance.save_mongodb_to_csv(insert_id)
        return {"message": "successfully saved admin account log to csv"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/get/unused/service/account")
async def get_unused_service_account(days_threshold: int):
    try:
        result, inserted_id = await gcp_compliance.get_unused_service_account(gcp_credentials, gcp_project_id, days_threshold)
        res_json = bson_to_json({
            "result": result,
            "inserted_id": inserted_id
        })
        return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(path="/disable/unused/service/account")
async def disable_unused_service_accounts(inserted_id: str):
    try:
        await gcp_compliance.disable_unused_service_accounts(gcp_credentials, gcp_project_id, inserted_id)
        return {"message": "successfully disabled service accounts"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(path="/delete/unused/service/account")
async def delete_unused_service_accounts(inserted_id: str):
    try:
        await gcp_compliance.delete_unused_service_accounts(gcp_credentials, gcp_project_id, inserted_id)
        return {"message": "successfully deleted service accounts"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(path="/disable/unused/service/account/key")
async def disable_unused_service_account_keys(inserted_id: str):
    try:
        await gcp_compliance.disable_unused_service_account_keys(gcp_credentials, gcp_project_id, inserted_id)
        return {"message": "successfully disabled service account keys"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(path="/delete/unused/service/account/key")
async def delete_unused_service_account_keys(inserted_id: str):
    try:
        await gcp_compliance.delete_unused_service_account_keys(gcp_credentials, gcp_project_id, inserted_id)
        return {"message": "successfully deleted service account keys"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/list/keys/without/expiration")
async def list_keys_without_expiration():
    try:
        result, inserted_id = await gcp_compliance.list_keys_without_expiration(gcp_credentials, gcp_project_id)
        res_json = bson_to_json({
            "result": result,
            "inserted_id": inserted_id
        })
        return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/check/key/rotation")
async def check_key_rotation(days_threshold: int):
    try:
        result, inserted_id = await gcp_compliance.check_key_rotation(gcp_credentials, gcp_project_id, days_threshold)
        res_json = bson_to_json({
            "result": result,
            "inserted_id": inserted_id
        })
        return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(path="/disable/service/account/key")
async def disable_service_account_keys(inserted_id: str):
    try:
        await gcp_compliance.disable_keys_without_expiration(gcp_credentials, inserted_id)
        return {"message": "successfully disabled service account keys"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(path="/delete/service/account/key")
async def delete_service_account_keys(inserted_id: str):
    try:
        await gcp_compliance.delete_keys_without_expiration(gcp_credentials, inserted_id)
        return {"message": "successfully deleted service account keys"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(path="/create/new/service/account/key")
async def renew_old_keys(inserted_id: str):
    try:
        await gcp_compliance.renew_old_keys(gcp_credentials, inserted_id)
        return {"message": "successfully created service account keys"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(path="/get/admin/permission/member/count")
async def count_admins():
    try:
        result, inserted_id = await gcp_compliance.count_admins(gcp_credentials, gcp_project_id)
        res_json = bson_to_json({
            "result": result,
            "inserted_id": inserted_id
        })
        return JSONResponse(content=res_json, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))