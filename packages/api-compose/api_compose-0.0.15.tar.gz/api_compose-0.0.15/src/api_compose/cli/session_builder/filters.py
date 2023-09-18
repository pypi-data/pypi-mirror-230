from pathlib import Path
from typing import List, Set

from api_compose import get_logger
from api_compose.services.common.models.base import BaseModel

logger = get_logger(__name__)


def filter_by_inclusion(
        models: List[BaseModel],
        include_manifest_file_paths: List[Path],
        include_tags: List[str],
        include_models: List[str],
) -> List[BaseModel]:
    required_by_manifest_file_paths = [
        model for model in models if
        model.manifest_file_path in include_manifest_file_paths
    ]
    required_by_tags = [model for model in models if any(tag in include_tags for tag in model.tags)]
    required_by_models = [model for model in models if model.model_name in include_models]

    return list(set(required_by_manifest_file_paths + required_by_tags + required_by_models))


def filter_by_exclusion(
        models: List[BaseModel],
        exclude_manifest_file_paths: List[Path],
        exclude_tags: List[str],
        exclude_models: List[str],
) -> List[BaseModel]:
    models = list(filter(lambda x: False if x.manifest_file_path in exclude_manifest_file_paths else True, models))
    models = list(filter(lambda x: False if any(tag in exclude_tags for tag in x.tags) else True, models))
    models = list(filter(lambda x: False if x.model_name in exclude_models else True, models))

    return models
