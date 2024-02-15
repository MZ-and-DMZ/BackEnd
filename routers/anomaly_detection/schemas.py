from pydantic import BaseModel


class workingHours(BaseModel):
    group: str
    startTime: str
    endTime: str


class workingIP(BaseModel):
    ip: str