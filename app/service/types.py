from pydantic import BaseModel
from typing import Any

class RenderRequestBody(BaseModel):
    data: dict[str, Any]
