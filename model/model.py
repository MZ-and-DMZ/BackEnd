from pydantic import BaseModel


class Auth(BaseModel):
    id: str
    pwd: str


class Position(BaseModel):
    position_name: str
    type: str
    description: str
    aws_policies: list
    gcp_policies: list


class Users(BaseModel):
    username: str
    description: str
    aws_account: str
    gcp_account: str
    attached_position: list
    attached_group: list
    updatetime: str
