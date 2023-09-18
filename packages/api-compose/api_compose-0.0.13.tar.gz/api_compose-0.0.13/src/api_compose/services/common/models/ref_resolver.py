"""
Intermediate models with references still not yet resolved
"""
from pathlib import Path
from typing import Dict, Any, Literal

from pydantic import Field, AliasChoices, model_validator, field_validator

from api_compose.core.settings.settings import (GlobalSettingsModelSingleton)
from api_compose.core.utils.string import normalise_sentence
from api_compose.services.common.models.base import BaseModel


class RefResolverModel(BaseModel):
    model_name: Literal['RefResolverModel'] = Field(
        description=BaseModel.model_fields['model_name'].description
    )

    id: str = Field(
        '',
        description='Reference Path to a Manifest File',
        validation_alias=AliasChoices(
            'id',
            'ref',
        )
    )
    description: str = Field(
        '',
        description='BDD style description. Used to lookup the corresponding manifest file',
        validation_alias=AliasChoices(
            'description',
            'given',
            'when',
            'then'
        ),
    )

    manifests_folder_path: Path = Field(
        # get folder path dynamically with factory
        default_factory=lambda: GlobalSettingsModelSingleton.get().discovery.manifests_folder_path,
        description='Absolute Path to manifest files',
    )

    ## All Contexts
    env_vars_context: Dict[str, Any] = Field(
        {},
        description='Context from Env Var to render manifest file'
    )

    extra_context: Dict[str, Any] = Field(
        {},
        validation_alias=AliasChoices(
            'extra_context',
            'context',
        ),
        description='Context specific to the model to render manifest file'
    )

    cli_context: Dict[str, Any] = Field(
        {},
        description='Context from CLI used to render manifest file'
    )


    @field_validator('description', mode='after')
    @classmethod
    def validate_description(cls, value) -> str:
        return normalise_sentence(value)

    @model_validator(mode='after')
    @classmethod
    def validate_id_and_description(cls, m: 'RefResolverModel') -> 'RefResolverModel':
        m.id = m.id.strip()
        m.description = m.description.strip()
        if (len(m.id) > 0 and len(m.description) > 0):
            raise ValueError('Manifest Path and GIVEN-WHEN-THEN cannot be set simultaneously')

        if (len(m.id) == 0 and len(m.description) == 0):
            raise ValueError('Manifest Path and GIVEN-WHEN-THEN cannot be both empty simultaneously')

        return m
