from typing import Any, List, Optional

from pydantic import BaseModel


class auth(BaseModel):
    id: str
    password: str


class position(BaseModel):
    positionName: str
    description: Optional[str]
    csp: str
    policies: List[str]


class updatePosition(BaseModel):
    description: str
    policies: List[str]


class user(BaseModel):
    userName: str
    department: str
    duty: str
    description: str
    awsAccount: Optional[str]
    gcpAccount: Optional[str]
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


class recommendParams(BaseModel):
    actions: List[str]


class notification(BaseModel):
    type: str
    title: str
    content: str
    detail: Any
