__all__ = ['set_custom_selector']

from pathlib import Path
from typing import List, Set

from api_compose.core.logging import get_logger
from api_compose.core.settings.exceptions import IncludeExcludeBothSetException
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.core.settings.settings import SelectorsSettings

logger = get_logger(__name__)


def set_custom_selector_pack(
        include_manifest_file_paths: List[Path],
        include_tags: List[str],
        include_models: List[str],
        exclude_manifest_file_paths: List[Path],
        exclude_tags: List[str],
        exclude_models: List[str],
) -> None:
    """

    Returns
    -------
    object
    """
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
        logger.info('Overriding selectors pack to `custom`')
        GlobalSettingsModelSingleton.get().cli_options.selectors_pack_name = 'custom'
        GlobalSettingsModelSingleton.get().selectors.packs.append(SelectorsSettings.SelectorsPackSettings(
            name='custom',
            type='Include',
            manifest_file_paths=include_manifest_file_paths,
            tags=include_tags,
            models=include_models, )
        )
    elif exclude_num > 0:
        logger.info('Overriding selectors pack to `custom`')
        GlobalSettingsModelSingleton.get().cli_options.selectors_pack_name = 'custom'
        GlobalSettingsModelSingleton.get().selectors.packs.append(SelectorsSettings.SelectorsPackSettings(
            type='Exclude',
            manifest_file_paths=exclude_manifest_file_paths,
            tags=exclude_tags,
            models=exclude_models,
        ))
    else:
        pass
