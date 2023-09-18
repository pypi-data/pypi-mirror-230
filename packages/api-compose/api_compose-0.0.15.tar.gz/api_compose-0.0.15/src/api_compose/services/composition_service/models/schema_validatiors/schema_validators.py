from typing import Optional, Dict, List, Union, Any, Literal

from lxml import etree
from lxml.etree import ElementBase
from pydantic import Field, ConfigDict

from api_compose.core.lxml.parser import get_default_schema, PrintableElementAnnotation, get_default_element
from api_compose.services.common.models.base import BaseModel


class BaseSchemaValidatorModel(BaseModel):

    model_name: Literal['BaseSchemaValidatorModel'] = Field(
        'BaseSchemaValidatorModel',
        description=BaseModel.model_fields['model_name'].description
    )

    # Expected Schema
    schema_id: str = Field(
        description='Id of the schema used for comparison',
    )

    expected_schema: Any = Field(
        None,
        description='Schema used to validate an object'
    )

    # Actual Object
    json_path: str = Field(
        '$',
        description='json path from output to destined object for comparison'
    )
    actual: Any = Field(
        None,
        description='Actual object to be validated'
    )

    exec: Optional[str] = Field(None, description='Exception while validating schema')
    is_valid: bool = Field(False, description='Whether the object is valid')


class JsonSchemaValidatorModel(BaseSchemaValidatorModel):
    model_name: Literal['JsonSchemaValidatorModel'] = Field(
        description=BaseSchemaValidatorModel.model_fields['model_name'].description
    )
    # Expected Schema
    expected_schema: Dict = Field(
        {},
        description=BaseSchemaValidatorModel.model_fields['expected_schema'].description
    )

    # Actual Object
    actual: Union[List, Dict] = Field(
        {},
        description=BaseSchemaValidatorModel.model_fields['actual'].description
    )


class XmlSchemaValidatorModel(BaseSchemaValidatorModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_name: Literal['XmlSchemaValidatorModel'] = Field(
        description=BaseSchemaValidatorModel.model_fields['model_name'].description
    )

    # Expected Schema
    expected_schema: PrintableElementAnnotation = Field(
        get_default_schema(),
        description=BaseSchemaValidatorModel.model_fields[
            'expected_schema'].description
    )

    # Actual Object
    actual: ElementBase = Field(
        get_default_element(),
        description=BaseSchemaValidatorModel.model_fields['actual'].description
    )
