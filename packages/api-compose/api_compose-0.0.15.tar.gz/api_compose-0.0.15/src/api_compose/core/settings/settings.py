"""
Programme's Global Settings.

Cannot use logger. That would cause Cyclical Dependency OR double or triple logging of the same message
"""

__all__ = ['GlobalSettingsModelSingleton', 'GlobalSettingsModel']

import logging
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Set, Any, Literal, Annotated

from pydantic import Field, model_validator, computed_field, PlainSerializer, field_validator

from api_compose.core.annotations import JsonSerialisablePathAnnotation
from api_compose.core.events.base import EventType
from api_compose.core.settings.yaml_settings import YamlBaseSettings, BaseSettings, SettingsConfigDict
from api_compose.services.persistence_service.models.enum import BackendProcessorEnum
from api_compose.services.reporting_service.models.enum import ReportProcessorEnum

CONFIGURATION_FILE_PATH = Path.cwd().joinpath('config.yaml')


class ActionSettings(BaseSettings):
    pass


class BackendSettings(BaseSettings):
    processor: Annotated[
        BackendProcessorEnum,
        PlainSerializer(lambda x: x.value, return_type=str, when_used='always'),
    ] = BackendProcessorEnum.SimpleBackend


class CliOptions(BaseSettings):
    """Container to store all Options passed via CLI by user"""
    is_interactive: bool = Field(False,
                                 description='When True, users will be prompted to create assertions dynamically at the end of each Scenario Run')
    cli_context: Dict[str, Any] = Field({}, description='context passed via CLI')
    include_manifest_file_paths: List[JsonSerialisablePathAnnotation] = Field([],
                                                                              description='List of manifest file paths to include')
    include_tags: List[str] = Field([], description='set of tags to look for in manifest(s) to include')
    include_models: List[str] = Field([], description='list of models to look for in manifest(s) to include')

    exclude_manifest_file_paths: List[JsonSerialisablePathAnnotation] = Field([],
                                                                              description='List of manifest file paths to exclude')
    exclude_tags: List[str] = Field([], description='set of tags to look for in manifest(s) to exclude')
    exclude_models: List[str] = Field([], description='list of models to look for in manifest(s) to exclude')
    selectors_pack_name: Optional[str] = Field('', description='selectors pack name')
    env_files_pack_name: Optional[str] = Field('', description='env files pack name')

    @field_validator('include_tags', 'exclude_tags', mode='before')
    @classmethod
    def validate_tags(cls, values):
        if type(values) == list:
            values = list(set(values))
        return values


class DiscoverySettings(BaseSettings):
    manifests_folder_path: JsonSerialisablePathAnnotation = Path('manifests')
    functions_folder_path: JsonSerialisablePathAnnotation = Path('functions')
    macros_folder_path: JsonSerialisablePathAnnotation = Path('macros')


class EnvFilesSettings(BaseSettings):
    class EnvFilesPackSettings(BaseSettings):
        name: str = Field(description='Name of the pack')
        paths: List[JsonSerialisablePathAnnotation] = Field(description='Ordered List of env files')

    default: str = Field(
        'base',
        description='Default Pack of env files to use',
    )
    packs: List[EnvFilesPackSettings] = Field(
        [
            EnvFilesPackSettings(name='base', paths=[Path('envs/base-env.yaml')]),
            EnvFilesPackSettings(name='uat', paths=[Path('envs/base-env.yaml'), Path('envs/uat-env.yaml')]),
            EnvFilesPackSettings(name='prod', paths=[Path('envs/base-env.yaml'), Path('envs/prod-env.yaml')]),
        ],
        description='Mapping of pack to a list of env files'
    )

    @model_validator(mode='after')
    @classmethod
    def validate_pack(cls, m: 'EnvFilesSettings'):
        if len(set([pack.name for pack in m.packs])) != len([pack.name for pack in m.packs]):
            raise ValueError('Packs with the same name found!')

        return m


class SelectorsSettings(BaseSettings):
    class SelectorsPackSettings(BaseSettings):
        name: str = Field(description='Name of the pack')
        type: Literal['Include', 'Exclude', 'Notset']
        manifest_file_paths: List[JsonSerialisablePathAnnotation] = Field([],
                                                                          description='List of manifest file paths. Path must be relative to the manifest folder')
        tags: List[str] = Field([], description='set of tags to look for in manifest(s)')
        models: List[str] = Field([], description='list of models to look for in manifest(s)')

        @field_validator('tags',  mode='before')
        @classmethod
        def validate_tags(cls, values):
            if type(values) == list:
                values = list(set(values))
            return values

    default: str = Field(
        'spec',
        description='Current selector',
    )

    packs: List[SelectorsPackSettings] = Field(
        [
            SelectorsPackSettings(
                name='spec',
                type='Include',
                models=['SpecificationModel']
            ),
            SelectorsPackSettings(
                name='action',
                type='Include', models=[
                    'JsonHttpActionModel',
                    'XmlHttpActionModel']
            ),
        ]
        ,
        description='Mapping of pack to a list of env files'
    )

    @model_validator(mode='after')
    @classmethod
    def validate_pack(cls, m: 'SelectorsSettings'):
        if len(set([pack.name for pack in m.packs])) != len([pack.name for pack in m.packs]):
            raise ValueError('Packs with the same name found!')

        return m


class LoggingSettings(BaseSettings):
    logging_level: int = logging.INFO
    log_file_path: Optional[JsonSerialisablePathAnnotation] = Path('log.jsonl')
    event_filters: List[EventType] = []


class ReportingSettings(BaseSettings):
    processor: Annotated[
        ReportProcessorEnum,
        PlainSerializer(lambda x: x.value, return_type=str, when_used='always')
    ] = ReportProcessorEnum.HtmlReport
    reports_folder: JsonSerialisablePathAnnotation = Path('build/reports')


class GlobalSettingsModel(YamlBaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        yaml_file="config.yaml",
        env_prefix='acp__',
        extra='forbid'
    )

    action: ActionSettings = ActionSettings()
    backend: BackendSettings = BackendSettings()
    cli_options: CliOptions = Field(CliOptions())
    compiled_folder: JsonSerialisablePathAnnotation = Path('build/compiled')
    discovery: DiscoverySettings = DiscoverySettings()
    env_files: EnvFilesSettings = EnvFilesSettings()
    logging: LoggingSettings = LoggingSettings()
    reporting: ReportingSettings = ReportingSettings()
    run_folder: JsonSerialisablePathAnnotation = Path('build/run')
    selectors: SelectorsSettings = SelectorsSettings()
    session_id: str = Field(
        # ensures uniquenes of session when action is saved to database
        str(uuid.uuid4()),
        description='Unique Identifier of session. For internal use only',
        exclude=True
    )

    @computed_field
    @property
    def current_env_files_pack_name(self) -> str:
        return self.env_files.default if not self.cli_options.env_files_pack_name else self.cli_options.env_files_pack_name

    @computed_field
    @property
    def current_selectors_pack_name(self) -> str:
        return self.selectors.default if not self.cli_options.selectors_pack_name else self.cli_options.selectors_pack_name

    @property
    def current_env_files_pack(self) -> EnvFilesSettings.EnvFilesPackSettings:
        env_files_packs = [pack for pack in self.env_files.packs if pack.name == self.current_env_files_pack_name]
        if len(env_files_packs) == 0:
            raise ValueError(f'No env files pack named **{self.current_env_files_pack_name}** is found! \n'
                             f'Available env files packs are {[pack.name for pack in self.env_files.packs]}')

        env_files_pack = env_files_packs[0]
        for path in env_files_pack.paths:
            assert path.exists(), f"Error - Env File Pack {env_files_pack.name} contains non-existent env file {path.absolute()}"

        return env_files_pack

    @property
    def current_selectors_pack(self) -> SelectorsSettings.SelectorsPackSettings:
        selector_packs = [pack for pack in self.selectors.packs if pack.name == self.current_selectors_pack_name]
        if len(selector_packs) == 0:
            raise ValueError(f'No selector pack named **{self.current_selectors_pack_name}** is found! \n'
                             f'Available selectors are {[pack.name for pack in self.selectors.packs]}')
        else:
            return selector_packs[0]


class GlobalSettingsModelSingleton():
    _GLOBAL_SETTINGS_MODEL: Optional[GlobalSettingsModel] = None

    @classmethod
    def set(cls):
        cls._GLOBAL_SETTINGS_MODEL = GlobalSettingsModel()

    @classmethod
    def get(cls) -> GlobalSettingsModel:
        if cls._GLOBAL_SETTINGS_MODEL is None:
            raise ValueError('Global Settings Model not yet created!')
        return cls._GLOBAL_SETTINGS_MODEL
