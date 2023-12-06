from typing import List

from pydantic import BaseModel


class group(BaseModel):
    groupName: str
    description: str
    users: List[str]
    attachedPosition: List[str]


class updateGroup(BaseModel):
    description: str
    users: List[str]
    attachedPosition: List[str]
