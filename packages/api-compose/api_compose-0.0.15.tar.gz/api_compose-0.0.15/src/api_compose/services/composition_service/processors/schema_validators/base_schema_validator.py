__all__ = ["BaseSchemaValidator"]

import traceback
from abc import ABC, abstractmethod
from typing import List

from api_compose.core.logging import get_logger
from api_compose.core.utils.exceptions import NoMatchesFoundWithFilter
from api_compose.core.utils.json_path import parse_json_with_jsonpath
from api_compose.services.common.processors.base import BaseProcessor
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.composition_service.events.schema_validator import SchemaValidatorEvent
from api_compose.services.composition_service.models.actions.outputs.base_outputs import BaseActionOutputModel
from api_compose.services.composition_service.models.actions.schemas import BaseSchemaModel
from api_compose.services.composition_service.models.schema_validatiors.schema_validators import \
    BaseSchemaValidatorModel

logger = get_logger(__name__)


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.SchemaValidator,
    models=[
        BaseSchemaValidatorModel(id='200', schema_id='200'),
    ]
)
class BaseSchemaValidator(BaseProcessor, ABC):
    """
    validate

    """

    def __init__(
            self,
            schema_models: List[BaseSchemaModel],
            schema_validator_model: BaseSchemaValidatorModel,
            action_output_model: BaseActionOutputModel,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.schema_models = schema_models
        self.schema_validator_model = schema_validator_model
        self.action_output_model = action_output_model
        self.is_setup_success = False

    def _set_actual(self):
        """
        Set the actual object to be schema-validated
        """
        self.actual = parse_json_with_jsonpath(
            self.action_output_model.model_dump(),
            self.schema_validator_model.json_path
        )
        self.schema_validator_model.actual = self.actual

    def _set_expected_schema(self):
        """
        Set the expected schema used for validation.

        - self.expected_schema_model
        - self.expected_schema
        """
        target_schema_id = self.schema_validator_model.schema_id
        is_found = False

        # Expected Schema lookup
        for schema_model in self.schema_models:
            if schema_model.id == target_schema_id:
                self.expected_schema_model = schema_model
                is_found = True

        if not is_found:
            logger.error(f'No schema has the schema_id {target_schema_id=}')
            raise NoMatchesFoundWithFilter(filter={'id': target_schema_id}, collection=self.schema_models)

        # Render schema
        self.expected_schema = self.expected_schema_model.schema_.deserialise_to_obj().obj
        self.schema_validator_model.expected_schema = self.expected_schema

    @abstractmethod
    def validate(self):
        try:
            self._set_actual()
            self._set_expected_schema()
        except Exception as e:
            logger.error(traceback.format_exc(), SchemaValidatorEvent())
            self.schema_validator_model.exec = traceback.format_exc()
            self.schema_validator_model.is_valid = False
            self.is_setup_success = False
        else:
            self.is_setup_success = True


