from typing import Any, List, Optional

from pydantic import BaseModel


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
