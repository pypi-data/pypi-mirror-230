from typing import List, Union, Annotated

from pydantic import Field

from api_compose.services.composition_service.models.schema_validatiors.schema_validators import \
    JsonSchemaValidatorModel, XmlSchemaValidatorModel

XmlHttpActionModelSchemaAnnotation = List[
    Annotated[Union[JsonSchemaValidatorModel, XmlSchemaValidatorModel],
    Field(discriminator='model_name')]
]

XmlHttpActionModelSchemaValidatorAnnotation = XmlHttpActionModelSchemaAnnotation
