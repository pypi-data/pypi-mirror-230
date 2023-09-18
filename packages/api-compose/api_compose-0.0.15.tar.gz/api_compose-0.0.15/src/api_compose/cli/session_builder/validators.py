from typing import List, Set

from api_compose.services.common.exceptions import ModelNotFoundException, TagNotFoundException
from api_compose.services.common.registry.processor_registry import ProcessorRegistry


def validate_model_names(
        model_names: List[str]
):
    available_model_names = ProcessorRegistry.get_available_model_names()
    for model_name in model_names:
        if model_name not in available_model_names:
            raise ModelNotFoundException(
                target_model=model_name,
                available_models=available_model_names
            )


def validate_tags(
        tags: List[str],
        available_tags: List[str],
):
    for tag in tags:
        if tag not in available_tags:
            raise TagNotFoundException(tag, available_tags)
