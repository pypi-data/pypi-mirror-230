from typing import Optional, Dict, List, Union, Any, Literal

from pydantic import Field

from api_compose.services.common.models.base import BaseModel


class BaseSchemaValidatorModel(BaseModel):


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
    pass
