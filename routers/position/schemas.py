from typing import List, Optional

from pydantic import BaseModel


class position(BaseModel):
    positionName: str
    description: Optional[str]
    csp: str
    policies: List[str]


class updatePosition(BaseModel):
    description: str
    policies: List[str]
