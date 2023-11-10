from typing import List

from pydantic import BaseModel


class auth(BaseModel):
    id: str
    password: str


class position(BaseModel):
    positionName: str
    description: str
    csp: str
    policies: List[dict]


class updatePosition(BaseModel):
    description: str
    policies: List[dict]


class user(BaseModel):
    userName: str
    department: str
    duty: str
    description: str
    awsAccount: str
    gcpAccount: str
    attachedPosition: List[str]
    attachedGroup: List[str]


class updateUser(BaseModel):
    department: str
    duty: str
    description: str
    awsAccount: str
    gcpAccount: str
    attachedPosition: List[str]
    attachedGroup: List[str]


class group(BaseModel):
    groupName: str
    description: str
    users: List[str]
    attachedPosition: List[str]


class updateGroup(BaseModel):
    description: str
    users: List[str]
    attachedPosition: List[str]
