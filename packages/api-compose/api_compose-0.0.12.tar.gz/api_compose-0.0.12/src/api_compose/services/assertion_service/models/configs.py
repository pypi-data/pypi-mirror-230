from typing import Callable

from pydantic import BaseModel as _BaseModel, Field


class BaseAssertionConfigModel(_BaseModel):
    pass


class JinjaAssertionConfigModel(BaseAssertionConfigModel):
    template: str = Field('', description='Renderable core template content')
