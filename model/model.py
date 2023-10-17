from typing import List

from pydantic import BaseModel


class Auth(BaseModel):
    id: str
    password: str


class Position(BaseModel):
    positionName: str
    isCustom: bool = True
    description: str
    awsPolicies: List[str]
    gcpPolicies: List[str]


class Users(BaseModel):
    userName: str
    description: str
    awsAccount: str
    gcpAccount: str
    attachedPosition: list
    attachedGroup: list
    updatetime: str
