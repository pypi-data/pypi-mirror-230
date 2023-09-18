__all__ = ["JsonSchemaValidator"]

import traceback
from abc import ABC

import jsonschema

from api_compose.core.logging import get_logger
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.composition_service.events.schema_validator import SchemaValidatorEvent
from api_compose.services.composition_service.models.schema_validatiors.schema_validators import \
    JsonSchemaValidatorModel
from api_compose.services.composition_service.processors.schema_validators.base_schema_validator import \
    BaseSchemaValidator

logger = get_logger(__name__)


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.SchemaValidator,
    models=[
        JsonSchemaValidatorModel(
            model_name='JsonSchemaValidatorModel',
            id='OK',
            schema_id='200'
        ),
    ]
)
class JsonSchemaValidator(BaseSchemaValidator, ABC):
    """
    validate

    """

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

    def validate(self):
        super().validate()
        if self.is_setup_success:
            self.schema_validator_model.actual = self.actual

            try:
                jsonschema.validate(
                    self.actual,
                    self.expected_schema
                )
            except Exception as e:
                logger.error(traceback.format_exc(), SchemaValidatorEvent())
                self.schema_validator_model.exec = traceback.format_exc()
                self.schema_validator_model.is_valid = False
            else:
                logger.debug(f"Schema is valid - {self.actual=}", SchemaValidatorEvent())
                self.schema_validator_model.is_valid = True



