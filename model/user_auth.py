from pydantic import BaseModel


class UserAuth(BaseModel):
    id: str
    pwd: str
