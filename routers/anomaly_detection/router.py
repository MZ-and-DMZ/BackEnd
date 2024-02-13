from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.database import mongodb
from src.utils import bson_to_json
# from src.anomaly_detection_setting import str_to_time, time_to_str

router = APIRouter(prefix="/anomaly/detection", tags=["anomaly detection"])


@router.get(path="/timelist")
async def time_list():
    collection = mongodb.db["anomalyDetectionTime"]
    try:
        time_list = await collection.find({}).to_list(None)

        for item in time_list:
            item.pop("_id")
            # item["startTime"] = time_to_str(item["startTime"])
            # item["endTime"] = time_to_str(item["endTime"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"time_list": bson_to_json(time_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.post(path="/time/set")
async def set_time(group: str, start_time: str, end_time: str):
    collection = mongodb.db["anomalyDetectionTime"]
    try:
        # 시작 시간과 종료 시간을 파싱하여 datetime 객체로 변환
        # start_time = str_to_time(start_time)
        # end_time = str_to_time(end_time)

        query_result = await collection.insert_one(
            {"group": group, "startTime": start_time, "endTime": end_time}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": "Time range set successfully"},
            status_code=200,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to set")


@router.get(path="/iplist")
async def ip_list():
    collection = mongodb.db["anomalyDetectionIP"]
    try:
        ip_list = await collection.find({}).to_list(None)

        for item in ip_list:
            item.pop("_id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res_json = {"ip_list": bson_to_json(ip_list)}

    return JSONResponse(content=res_json, status_code=200)


@router.post(path="/ip/set")
async def set_ip(ip: str):
    collection = mongodb.db["anomalyDetectionIP"]
    try:
        query_result = await collection.insert_one(
            {"IP": ip}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if query_result.acknowledged:
        return JSONResponse(
            content={"message": "ip set successfully"},
            status_code=200,
        )
    else:
        raise HTTPException(status_code=500, detail="failed to set")