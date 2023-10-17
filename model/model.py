from typing import List

from pydantic import BaseModel


class auth(BaseModel):
    id: str
    password: str


class position(BaseModel):
    positionName: str
    isCustom: bool = True
    description: str
    csp: str
    policies: List[str]


class user(BaseModel):
    userName: str
    description: str
    awsAccount: str
    gcpAccount: str
    attachedPosition: list
    attachedGroup: list
    updatetime: str
