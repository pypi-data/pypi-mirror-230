from pydantic import BaseModel, Field


class BaseActionOutputModel(BaseModel):
    status_code: int = Field(
        -1,
        description="status code",
    )
