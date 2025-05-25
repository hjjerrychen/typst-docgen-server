from pydantic import BaseModel
class RenderRequestBody(BaseModel):
    data: dict[str, any]
