import json
from pathlib import Path
from typing import List, Set, Optional

from api_compose import DiscoveryEvent, get_env_vars_context
from api_compose.cli.session_builder.filters import filter_by_exclusion, filter_by_inclusion
from api_compose.cli.session_builder.selectors import set_custom_selector_pack
from api_compose.cli.session_builder.validators import validate_model_names, validate_tags
from api_compose.cli.utils.parser import parse_context
from api_compose.core.logging import get_logger
from api_compose.core.settings.settings import CliOptions, SelectorsSettings, EnvFilesSettings
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.root import SessionModel
from api_compose.root.models.scenario import ScenarioModel
from api_compose.root.models.specification import SpecificationModel
from api_compose.services.common.deserialiser import get_available_models
from api_compose.services.common.deserialiser.deserialiser import get_manifest_relative_path
from api_compose.services.common.models.base import BaseModel
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel

logger = get_logger(__name__)


def init_cli_settings(
        include_manifest_file_paths: List[Path],
        include_tags: List[str],
        include_models: List[str],
        exclude_manifest_file_paths: List[Path],
        exclude_tags: List[str],
        exclude_models: List[str],
        selectors_pack_name: Optional[str],
        env_files_pack_name: Optional[str],
        is_interactive: bool,
        ctx: List[str],
):
    """Set User-defined options to CliOptionsSettingsModel"""
    manifests_folder_path = GlobalSettingsModelSingleton.get().discovery.manifests_folder_path
    include_manifest_file_paths = [get_manifest_relative_path(manifests_folder_path, include_path) for include_path in include_manifest_file_paths]
    exclude_manifest_file_paths = [get_manifest_relative_path(manifests_folder_path, exclude_path) for exclude_path in exclude_manifest_file_paths]

    # Step 1: set CLI Options
    GlobalSettingsModelSingleton.get().cli_options = CliOptions(
        cli_context=parse_context(ctx),
        is_interactive=is_interactive,
        include_manifest_file_paths=include_manifest_file_paths,
        include_tags=include_tags,
        include_models=include_models,
        exclude_manifest_file_paths=exclude_manifest_file_paths,
        exclude_tags=exclude_tags,
        exclude_models=exclude_models,
        selectors_pack_name=selectors_pack_name,
        env_files_pack_name=env_files_pack_name
    )

    # Step 2: set custom selector pack
    set_custom_selector_pack(
        include_manifest_file_paths=GlobalSettingsModelSingleton.get().cli_options.include_manifest_file_paths,
        include_tags=GlobalSettingsModelSingleton.get().cli_options.include_tags,
        include_models=GlobalSettingsModelSingleton.get().cli_options.include_models,
        exclude_manifest_file_paths=GlobalSettingsModelSingleton.get().cli_options.exclude_manifest_file_paths,
        exclude_tags=GlobalSettingsModelSingleton.get().cli_options.exclude_tags,
        exclude_models=GlobalSettingsModelSingleton.get().cli_options.exclude_models,
    )

    # Display Env files Pack Name and Env Var
    logger.debug(f'Display Current Env Files Pack: {GlobalSettingsModelSingleton.get().current_env_files_pack_name}', DiscoveryEvent())
    logger.debug('Display Environment Variables:', DiscoveryEvent())
    logger.debug(json.dumps(
        get_env_vars_context([path for path in GlobalSettingsModelSingleton.get().current_env_files_pack.paths]),
        indent=4),
        DiscoveryEvent()
    )

    # Display Selector Pack Name var
    logger.debug(f'Display Current Selector Pack: {GlobalSettingsModelSingleton.get().current_selectors_pack_name}', DiscoveryEvent())


def parse_models(
        manifests_folder_path: Path,
        selectors_pack: SelectorsSettings.SelectorsPackSettings,
        env_files_pack: EnvFilesSettings.EnvFilesPackSettings,
) -> List[BaseModel]:
    """Parse manifest files, filter them and return required models"""
    env_vars_context = get_env_vars_context([path for path in env_files_pack.paths])

    # Step 3: Get Available Models
    available_models = get_available_models(
        manifests_folder_path,
        env_vars_context=env_vars_context,
        cli_context=dict(GlobalSettingsModelSingleton.get().cli_options.cli_context),
    )

    # Step 3: Validate
    validate_model_names(model_names=selectors_pack.models)
    validate_tags(tags=selectors_pack.tags, available_tags=sum([list(model.tags) for model in available_models], []))

    # Step 4: Filter them
    if selectors_pack.type == 'Include':
        required_models = filter_by_inclusion(
            models=available_models,
            include_manifest_file_paths=selectors_pack.manifest_file_paths,
            include_tags=selectors_pack.tags,
            include_models=selectors_pack.models,
        )
    else:
        required_models = filter_by_exclusion(
            models=available_models,
            exclude_manifest_file_paths=selectors_pack.manifest_file_paths,
            exclude_tags=selectors_pack.tags,
            exclude_models=selectors_pack.models,
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
                actions=[model],
                model_name='ScenarioModel',
            )
            specification_model = SpecificationModel(
                id=f"{specification_id_prefix}_{base_id}",
                description=f"{specification_description_prefix} - {base_description}",
                scenarios=[scenario_model],
                model_name='SpecificationModel',
            )
            specification_models.append(specification_model)
        elif isinstance(model, ScenarioModel):
            specification_model = SpecificationModel(
                id=f"{specification_id_prefix}_{base_id}",
                description=f"{specification_description_prefix} - {base_description}",
                scenarios=[model],
                model_name='SpecificationModel',
            )
            specification_models.append(specification_model)
        elif isinstance(model, SpecificationModel):
            specification_models.append(model)
        else:
            raise ValueError(f'Unhandled model type {type(model)}')

    session_model = SessionModel(
        id=GlobalSettingsModelSingleton.get().session_id,
        specifications=specification_models,
        model_name='SessionModel',
    )

    return session_model
