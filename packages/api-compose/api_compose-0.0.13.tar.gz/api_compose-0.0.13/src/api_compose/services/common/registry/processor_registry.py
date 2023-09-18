from enum import Enum
from typing import Type, Callable, List, Optional, Dict

from pydantic import BaseModel as _BaseModel
from pydantic import Field

from api_compose.core.logging import get_logger
from api_compose.services.common.exceptions import ModelNotFoundException, ProcessorNotFoundException, \
    ProcessorNonUniqueException
from api_compose.services.common.models.base import BaseModel
from api_compose.services.common.processors.base import BaseProcessor, BaseProcessorSubclass

logger = get_logger(__name__)


class ProcessorCategory(str, Enum):
    Action = 'Action'
    Adapter = 'Adapter'
    Assertion = 'Assertion'
    Backend = 'Backend'

    Executor = 'Executor'
    SchemaValidator = 'SchemaValidator'
    RefResolver = 'RefResolver'
    Reporting = 'Reporting'

    # for testing only
    _Unknown = 'Unknown'


class ProcessorRegistryEntry(_BaseModel, extra='forbid'):
    processor_class: Type[BaseProcessor]
    category: ProcessorCategory = Field(description='Category the asset belongs to')
    models: List[BaseModel] = Field(description='Example Models')

    @property
    def processor_class_name(self):
        return self.processor_class.__name__


class ProcessorRegistry:
    """
    Applied on Class
    """
    registry: List[ProcessorRegistryEntry] = []

    @classmethod
    def _validate_no_entry_with_same_class_name(cls, processor_class: Type):
        registered_entry_models = [entry for entry in cls.registry if
                                   entry.processor_class_name == processor_class.__name__]
        if len(registered_entry_models) > 0:
            raise ProcessorNonUniqueException(target_processor=processor_class.__name__)

    @classmethod
    def set(cls,
            models: List[BaseModel],
            processor_category: ProcessorCategory,

            ) -> Callable:

        def decorator(processor_class: Type[BaseProcessor]):
            cls._validate_no_entry_with_same_class_name(processor_class=processor_class)

            cls.registry.append(
                ProcessorRegistryEntry(
                    processor_class=processor_class,
                    category=processor_category,
                    models=models
                )
            )

            return processor_class

        return decorator

    @classmethod
    def create_processor_by_name(
            cls,
            class_name: str,
            config: Dict
    ) -> BaseProcessorSubclass:
        processor_class: Optional[Type[BaseProcessor]] = None
        for entry in cls.registry:
            if entry.processor_class_name == class_name:
                processor_class = entry.processor_class

        if processor_class is None:
            raise ProcessorNotFoundException(
                target_processor=class_name,
                available_processors=[entry.processor_class_name for entry in cls.registry]
            )
        else:
            return processor_class(**config)

    @classmethod
    def create_model_by_model_name(
            cls,
            model_name: Optional[str],
            config: Dict,
    ) -> BaseModel:

        available_models = {model.__class__.__name__: model for entry in cls.registry for model in entry.models}

        # Pick
        model = available_models.get(model_name)
        if model is None:
            raise ModelNotFoundException(target_model=model_name,
                                         available_models=[name for name in available_models.keys()])
        else:
            # here
            model = model.__class__(**config)

        return model

    @classmethod
    def get_available_model_names(
            cls,
    ) -> List[str]:
        return [model.__class__.__name__ for entry in cls.registry for model in entry.models]
