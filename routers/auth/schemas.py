from pydantic import BaseModel


class auth(BaseModel):
    id: str
    password: str
