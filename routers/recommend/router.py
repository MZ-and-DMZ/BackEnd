from fastapi import APIRouter, Body, HTTPException, Path
from fastapi.responses import JSONResponse

from .schemas import *
from .service import find_best_awsPolicy, find_best_gcpRole

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.post(path="/{csp}")
async def recommend(
    csp: str = Path(..., title="csp"), actions: recommendParams = Body(...)
):
    if csp == "aws":
        return await find_best_awsPolicy(set(actions.actions))
    elif csp == "gcp":
        return await find_best_gcpRole(set(actions.actions))
