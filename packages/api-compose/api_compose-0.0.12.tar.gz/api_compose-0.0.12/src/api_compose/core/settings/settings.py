"""
Programme's Global Settings.

Cannot use logger. That would cause Cyclical Dependency OR double or triple logging of the same message
"""

__all__ = ['GlobalSettingsModelSingleton', 'GlobalSettingsModel']

import logging
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Set, Any, Literal

from pydantic import Field, model_validator

from api_compose.core.events.base import EventType
from api_compose.core.settings.yaml_settings import YamlBaseSettings, BaseSettings, SettingsConfigDict
from api_compose.services.persistence_service.models.enum import BackendProcessorEnum
from api_compose.services.reporting_service.models.enum import ReportProcessorEnum


CONFIGURATION_FILE_PATH = Path.cwd().joinpath('config.yaml')


class ActionSettings(BaseSettings):
    pass


class BackendSettings(BaseSettings):
    processor: BackendProcessorEnum = BackendProcessorEnum.SimpleBackend


class CliOptions(BaseSettings):
    is_interactive: bool = Field(False,
                                 description='When True, users will be prompted to create assertions dynamically at the end of each Scenario Run')
    cli_context: Dict[str, Any] = Field({}, description='context passed via CLI')



class DiscoverySettings(BaseSettings):
    manifests_folder_path: Path = Path('manifests')
    functions_folder_path: Path = Path('functions')
    macros_folder_path: Path = Path('macros')


class EnvFilesSettings(BaseSettings):
    default: str = Field(
        'base',
        description='Default Pack of env files to use',
    )
    current: str = Field(
        '',
        description='Current Pack of env files to use',
        exclude=True
    )
    packs: Dict[str, List[Path]] = Field(
        {'base': [Path('envs/base-env.yaml')],
         'uat': [Path('envs/base-env.yaml'), Path('envs/uat-env.yaml')],
         'prod': [Path('envs/base-env.yaml'), Path('envs/prod-env.yaml')]
         },
        description='Mapping of pack to a list of env files'
    )

    @model_validator(mode='after')
    @classmethod
    def set_current_pack(cls, m: 'EnvFilesSettings'):
        if not m.current:
            m.current = m.default

        return m

class SelectorsSettings(BaseSettings):
    class SelectorPacksSettings(BaseSettings):
        type: Literal['Include', 'Exclude', 'Notset']
        manifest_file_paths: List[Path] = Field([], description='List of manifest file paths. Path must be relative to the manifest folder')
        tags: Set[str] = Field(set(), description='set of tags to look for in manifest(s)')
        models: List[str] = Field([], description='list of models to look for in manifest(s)')

    default: str = Field(
        'spec',
        description='Current selector',
        exclude=True
    )

    current: str = Field(
        '',
        description='Current selector',
        exclude=True
    )

    packs: Dict[str, SelectorPacksSettings] = Field(
        {
            'spec': SelectorPacksSettings(type='Include', models=['SpecificationModel']),
            'action': SelectorPacksSettings(type='Include', models=[
                'JsonHttpActionModel',
                'XmlHttpActionModel'
            ]),
        },
        description='Mapping of pack to a list of env files'
    )


    @model_validator(mode='after')
    @classmethod
    def set_current_pack(cls, m: 'SelectorsSettings'):
        if not m.current:
            m.current = m.default

        return m




class LoggingSettings(BaseSettings):
    logging_level: int = logging.INFO
    log_file_path: Optional[Path] = Path('log.jsonl')
    event_filters: List[EventType] = []



class ReportingSettings(BaseSettings):
    processor: ReportProcessorEnum = ReportProcessorEnum.HtmlReport
    reports_folder: Path = Path('build/reports')


class GlobalSettingsModel(YamlBaseSettings):
    action: ActionSettings = ActionSettings()
    backend: BackendSettings = BackendSettings()
    cli_options: CliOptions = Field(CliOptions())
    compiled_folder: Path = Path('build/compiled')
    discovery: DiscoverySettings = DiscoverySettings()
    env_files: EnvFilesSettings = EnvFilesSettings()
    logging: LoggingSettings = LoggingSettings()
    reporting: ReportingSettings = ReportingSettings()
    run_folder: Path = Path('build/run')
    selectors: SelectorsSettings = SelectorsSettings()
    session_id: str = Field(
        # ensures uniquenes of session when action is saved to database
        str(uuid.uuid4()),
        description='Unique Identifier of session. For internal use only',
        exclude=True
    )

    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        yaml_file="config.yaml",
        env_prefix='acp__',
        extra='forbid'
    )

    @property
    def all_env_files(self) -> List[Path]:
        env_file_paths: List[Path] = self.env_files.packs.get(self.env_files.current, [])
        env_file_paths = [
            env_file_path for env_file_path in env_file_paths if
            env_file_path.exists() and env_file_path.is_file()
        ]

        if len(env_file_paths) == 0:
            print(f'WARNING: No Env Files found in pack {self.env_files.current=}')

        return env_file_paths


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
