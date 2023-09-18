from enum import Enum
from typing import Optional

from pydantic import Field, BaseModel as _BaseModel


class AssertionStateEnum(str, Enum):
    PENDING = 'pending'
    EXECUTED = 'executed'


class JinjaAssertionModel(_BaseModel):
    description: str = Field(description='What this assertion is about')
    template: str

    state: AssertionStateEnum = Field(AssertionStateEnum.PENDING, description='State of the Assertion')
    is_success: bool = Field(False, description='whether the Assertion item is successful')
    exec: Optional[str] = Field(None, description='(If any) Exception raised when test item is executed')
    text: str = Field('', description='Text after template is rendered')