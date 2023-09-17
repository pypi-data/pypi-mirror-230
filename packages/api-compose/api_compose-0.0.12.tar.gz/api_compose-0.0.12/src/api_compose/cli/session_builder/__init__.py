from pathlib import Path
from typing import List, Set, Optional

from api_compose.cli.session_builder.filters import filter_by_exclusion, filter_by_inclusion
from api_compose.cli.session_builder.validators import validate_model_names, validate_tags
from api_compose.cli.utils.parser import parse_context
from api_compose.core.logging import get_logger
from api_compose.core.settings.exceptions import IncludeExcludeBothSetException
from api_compose.core.settings.settings import CliOptions, SelectorsSettings
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.root import SessionModel
from api_compose.root.models.scenario import ScenarioModel
from api_compose.root.models.specification import SpecificationModel
from api_compose.services.common.deserialiser import get_available_models
from api_compose.services.common.deserialiser.deserialiser import get_manifest_relative_path
from api_compose.services.common.models.base import BaseModel
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel

logger = get_logger(__name__)


def set_custom_selector_pack(
        include_manifest_file_paths: List[Path],
        include_tags: Set[str],
        include_models: List[str],
        exclude_manifest_file_paths: List[Path],
        exclude_tags: Set[str],
        exclude_models: List[str],
) -> None:
    include_num = len(include_tags) + len(include_manifest_file_paths) + len(include_models)
    exclude_num = len(exclude_tags) + len(exclude_manifest_file_paths) + len(exclude_models)

    if include_num > 0 and exclude_num > 0:
        raise IncludeExcludeBothSetException(
            include_manifest_file_paths=include_manifest_file_paths,
            include_tags=include_tags,
            include_models=include_models,
            exclude_manifest_file_paths=exclude_manifest_file_paths,
            exclude_tags=exclude_tags,
            exclude_models=exclude_models,
        )
    elif include_num > 0:
        logger.info('setting current selector to `custom`')
        GlobalSettingsModelSingleton.get().selectors.current = 'custom'
        GlobalSettingsModelSingleton.get().selectors.packs['custom'] = SelectorsSettings.SelectorPacksSettings(
            type='Include',
            manifest_file_paths=include_manifest_file_paths,
            tags=include_tags,
            models=include_models,
        )
    elif exclude_num > 0:
        logger.info('setting current selector to `custom`')
        GlobalSettingsModelSingleton.get().selectors.current = 'custom'
        GlobalSettingsModelSingleton.get().selectors.packs['custom'] = SelectorsSettings.SelectorPacksSettings(
            type='Exclude',
            manifest_file_paths=exclude_manifest_file_paths,
            tags=exclude_tags,
            models=exclude_models,
        )
    else:
        pass


def parse_models(
        manifests_folder_path: Path,
        include_manifest_file_paths: List[Path],
        include_tags: Set[str],
        include_models: List[str],
        exclude_manifest_file_paths: List[Path],
        exclude_tags: Set[str],
        exclude_models: List[str],
        selector: Optional[str],
        is_interactive: bool,
        ctx: List[str],
) -> List[BaseModel]:
    """Parse manifest files, filter them and return required models"""

    # Step 1: set CLI Options
    GlobalSettingsModelSingleton.get().cli_options = CliOptions(
        cli_context=parse_context(ctx),
        is_interactive=is_interactive
    )

    # Step 2: get current selector pack
    set_custom_selector_pack(
        include_manifest_file_paths=[
            get_manifest_relative_path(manifests_folder_path, include_path) for include_path in
            include_manifest_file_paths],
        include_tags=include_tags,
        include_models=include_models,
        exclude_manifest_file_paths=[
            get_manifest_relative_path(manifests_folder_path, exclude_path) for exclude_path in
            exclude_manifest_file_paths],
        exclude_tags=exclude_tags,
        exclude_models=exclude_models,
    )
    selector = GlobalSettingsModelSingleton.get().selectors.current

    # get from selector
    logger.info(f'Using selector {selector}')
    pack = GlobalSettingsModelSingleton.get().selectors.packs.get(selector)
    if not pack:
        raise ValueError(f'No selector pack named {selector} is found!')

    # Step 3: Get Available Models
    available_models = get_available_models(manifests_folder_path)

    # Step 3: Validate
    validate_model_names(model_names=pack.models)
    validate_tags(tags=pack.tags,
                  available_tags=set(sum([list(model.tags) for model in available_models], [])))

    # Step 4: Filter them
    if pack.type == 'Include':
        required_models = filter_by_inclusion(
            models=available_models,
            include_manifest_file_paths=pack.manifest_file_paths,
            include_tags=pack.tags,
            include_models=pack.models,
        )
    else:
        required_models = filter_by_exclusion(
            models=available_models,
            exclude_manifest_file_paths=pack.manifest_file_paths,
            exclude_tags=pack.tags,
            exclude_models=pack.models,
        )
    return required_models


def convert_models_to_session(models: List[BaseModel]) -> SessionModel:
    """
    Build SessionModel from any given BaseModel

    Parameters
    ----------
    models

    Returns
    -------

    """
    scenario_id_prefix = 'scen'
    specification_id_prefix = 'spec'

    scenario_description_prefix = 'Scenario'
    specification_description_prefix = 'Specification'

    specification_models: List[SpecificationModel] = []
    for idx, model in enumerate(models):
        model: BaseModel = model
        base_id = model.id
        base_description = model.description
        if isinstance(model, BaseActionModel):
            scenario_model = ScenarioModel(
                id=f"{scenario_id_prefix}_{base_id}",
                description=f"{scenario_description_prefix} - {base_description}",
                actions=[model]
            )
            specification_model = SpecificationModel(
                id=f"{specification_id_prefix}_{base_id}",
                description=f"{specification_description_prefix} - {base_description}",
                scenarios=[scenario_model]
            )
            specification_models.append(specification_model)
        elif isinstance(model, ScenarioModel):
            specification_model = SpecificationModel(
                id=f"{specification_id_prefix}_{base_id}",
                description=f"{specification_description_prefix} - {base_description}",
                scenarios=[model]
            )
            specification_models.append(specification_model)
        elif isinstance(model, SpecificationModel):
            specification_models.append(model)
        else:
            raise ValueError(f'Unhandled model type {type(model)}')

    session_model = SessionModel(
        id=GlobalSettingsModelSingleton.get().session_id,
        specifications=specification_models
    )

    return session_model
