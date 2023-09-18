from typing import Literal

from pydantic import Field

from api_compose.services.common.models.base import BaseModel
from api_compose.services.common.models.text_field.text_field import BaseTextField, JsonLikeTextField, XmlTextField


class BaseSchemaModel(BaseModel):
    model_name: Literal['BaseSchemaModel'] = Field(
        description=BaseModel.model_fields['model_name'].description
    )

    schema_: BaseTextField


class JsonSchemaModel(BaseSchemaModel):
    model_name: Literal['JsonSchemaModel'] = Field(
        description=BaseModel.model_fields['model_name'].description
    )
    schema_: JsonLikeTextField


class XmlSchemaModel(BaseSchemaModel):
    model_name: Literal['XmlSchemaModel'] = Field(
        description=BaseModel.model_fields['model_name'].description
    )
    schema_: XmlTextField
