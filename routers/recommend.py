from fastapi import APIRouter, Body, HTTPException, Path
from fastapi.responses import JSONResponse

from models import mongodb
from models.schemas import recommendParams
from src.util import bson_to_json

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.get(path="/{csp}")
async def recommend(
    csp: str = Path(..., title="csp"), actions: recommendParams = Body(...)
):
    if csp == "aws":
        pass
    elif csp == "gcp":
        pass
