from functools import cache
from pathlib import Path
from typing import List, Dict

import yaml
from yaml import ScalarEvent

from api_compose.core.utils.string import normalise_sentence
from api_compose.services.common.deserialiser.deserialiser import get_all_template_paths, deserialise_manifest_to_model
from api_compose.services.common.exceptions import ManifestDescriptionNonUniqueException
from api_compose.services.common.models.base import BaseModel


@cache
def get_available_models(manifests_folder_path: Path) -> List[BaseModel]:
    """
    Cached for whole session.
    Loop through al manifest templates, render them and deserialise to children of BaseModels.

    Parameters
    ----------
    manifests_folder_path

    Returns
    -------

    """
    models = []

    for template_path in get_all_template_paths(manifests_folder_path):
        models.append(
            deserialise_manifest_to_model(
                template_path,
                manifests_folder_path=manifests_folder_path,
                context=None,
            )
        )

    return models


@cache
def get_models_description(manifests_folder_path: Path) -> Dict[str, Path]:
    """
    Cached per whole session.
    Partial parse all manifests and extract the value of description

    Parameters
    ----------
    manifests_folder_path

    Returns
    -------

    """
    dict_ = {}
    target_key = 'description'

    manifests_folder_path = manifests_folder_path.absolute()

    for template_path in get_all_template_paths(manifests_folder_path):
        full_path = manifests_folder_path.joinpath(template_path)
        with open(full_path, 'r') as handle:
            get = False
            for event in yaml.parse(handle):
                if get:
                    value = getattr(event, 'value', None)
                    if value:
                        description = normalise_sentence(value)
                        existing_manifest_file_path = dict_.get(value)
                        current_manifest_file_path = template_path
                        if existing_manifest_file_path is not None:
                            raise ManifestDescriptionNonUniqueException(
                                offending_description=description,
                                offending_manifest_file_paths=[
                                    existing_manifest_file_path,
                                    current_manifest_file_path
                                ]
                            )
                        dict_[description] = template_path

                    break

                if type(event) == ScalarEvent and getattr(event, 'value', None) == target_key:
                    get = True

    return dict_
