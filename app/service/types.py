from pydantic import BaseModel
from typing import Any, Optional

class RenderRequestBody(BaseModel):
    data: dict[str, Any]
    allow_print: bool
