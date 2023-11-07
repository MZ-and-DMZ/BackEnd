from typing import List

from pydantic import BaseModel


class auth(BaseModel):
    id: str
    password: str


class position(BaseModel):
    positionName: str
    description: str
    csp: str
    policies: List[str]


class updatePosition(BaseModel):
    description: str
    policies: List[str]


class user(BaseModel):
    userName: str
    description: str
    awsAccount: str
    gcpAccount: str
    attachedPosition: List[str]
    attachedGroup: List[str]


class updateUser(BaseModel):
    description: str
    awsAccount: str
    gcpAccount: str
    attachedPosition: List[str]
    attachedGroup: List[str]


class group(BaseModel):
    groupName: str
    description: str
    awsGroup: str
    gcpGroup: str
    users: List[str]
    attachedPosition: List[str]
    updatetime: str
