from pydantic import BaseModel
from typing import List


class Auth(BaseModel):
    id: str
    pwd: str


class Position(BaseModel):
    position_name: str
    type: str = "custom"
    description: str
    aws_policies: List[str]
    gcp_policies: List[str]


class Users(BaseModel):
    user_id: str
    description: str
    aws_account: str
    gcp_account: str
    attached_position: list
    attached_group: list
    updatetime: str
