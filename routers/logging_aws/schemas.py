from pydantic import BaseModel


class SwitchState(BaseModel):
    state: bool
