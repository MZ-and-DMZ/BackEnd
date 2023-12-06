from typing import Any, List, Optional

from pydantic import BaseModel


class recommendParams(BaseModel):
    actions: List[str]
