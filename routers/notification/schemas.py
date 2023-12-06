from typing import Any

from pydantic import BaseModel


class notification(BaseModel):
    type: str
    title: str
    content: str
    detail: Any
