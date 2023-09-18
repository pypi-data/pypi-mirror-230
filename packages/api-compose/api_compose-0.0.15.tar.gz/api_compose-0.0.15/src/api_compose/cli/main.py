import os
import os
import shutil
from pathlib import Path
from typing import Annotated, List, Optional

from api_compose import FunctionsRegistry, safe_import_module
from api_compose.cli.commands import config
from api_compose.cli.events import DiscoveryEvent
from api_compose.cli.options import include_manifest_file_paths_option, include_tags_option, include_models_option, \
    exclude_manifest_file_paths_option, exclude_tags_option, exclude_models_option, is_interactive_option, \
    extra_env_var_option, env_files_pack_name_option, selector_pack_name_option
from api_compose.cli.session_builder import parse_models, convert_models_to_session, init_cli_settings
from api_compose.cli.utils.yaml_dumper import dump_dict_to_single_yaml_file
from api_compose.core.logging import get_logger
from api_compose.core.settings.settings import GlobalSettingsModelSingleton, SelectorsSettings
from api_compose.root import run_session_model
from api_compose.services.common.deserialiser.deserialiser import get_manifest_relative_path
from api_compose.services.common.exceptions import ManifestIdNotFoundException
from api_compose.services.common.registry.processor_registry import ProcessorRegistry
from api_compose.version import __version__

logger = get_logger(__name__)

import typer

COMPILED_FOLDER_PATH = GlobalSettingsModelSingleton.get().compiled_folder
COMPILED_FOLDER_PATH.mkdir(exist_ok=True, parents=True)
RUN_FOLDER_PATH = GlobalSettingsModelSingleton.get().run_folder
RUN_FOLDER_PATH.mkdir(exist_ok=True, parents=True)

OUTPUT_PATHS: List[Path] = [
    GlobalSettingsModelSingleton.get().run_folder,
    GlobalSettingsModelSingleton.get().compiled_folder,
    GlobalSettingsModelSingleton.get().reporting.reports_folder,
    GlobalSettingsModelSingleton.get().logging.log_file_path
]

DOCUMENTATION_URL = ""
EPILOG_TXT = rf"""
Doc: {DOCUMENTATION_URL}

Version: {__version__}

=============================================================

Configuration:  {Path.cwd().joinpath('config.yaml').absolute()}

=============================================================

Backend Processor: {GlobalSettingsModelSingleton.get().backend.processor.value}

Logging Level: {GlobalSettingsModelSingleton.get().logging.logging_level}

Log File Path: {GlobalSettingsModelSingleton.get().logging.log_file_path.absolute()}

Log Event Filters: {GlobalSettingsModelSingleton.get().logging.event_filters}

Manifests Folder Path: {GlobalSettingsModelSingleton.get().discovery.manifests_folder_path.absolute()}

Functions Folder Path: {GlobalSettingsModelSingleton.get().discovery.functions_folder_path.absolute()}

Reporting Processor: {GlobalSettingsModelSingleton.get().reporting.processor.value}

Reports Folder: {GlobalSettingsModelSingleton.get().reporting.reports_folder.absolute()}

Reporting Processor: {GlobalSettingsModelSingleton.get().reporting.processor.value}

Compiled Folder: {COMPILED_FOLDER_PATH.absolute()}

Run Folder: {RUN_FOLDER_PATH.absolute()}

=============================================================

Registered Jinja

=============================================================

{os.linesep.join(['- ' + entry.name + ' (alias: ' + os.linesep.join(entry.alias) + ') ' + os.linesep for entry in FunctionsRegistry.registry])}

=============================================================

Registered Models

=============================================================

{os.linesep.join(['- ' + name + os.linesep for name in ProcessorRegistry.get_available_model_names()])}



"""
HELP_TXT = "Declaratively Compose, Test and Report your API Calls"

app = typer.Typer(
    help=HELP_TXT,
    short_help=HELP_TXT,
    epilog=EPILOG_TXT,
    no_args_is_help=True,
)

app.add_typer(config.app, name='cfg', help="Configuration")


@app.callback()
def init_cli(
):
    """Initialise CLI. Must not throw exception """
    # Import JInja functions
    functions_folder_path = GlobalSettingsModelSingleton.get().discovery.functions_folder_path

    user_module = safe_import_module(functions_folder_path)
    if user_module is None:
        logger.info(f"Failed to Import Custom Functions from folder {functions_folder_path} does not exist",
                    DiscoveryEvent())

    # Import manifests
    manifests_folder_path = GlobalSettingsModelSingleton.get().discovery.manifests_folder_path
    if not manifests_folder_path.exists():
        logger.error(
            f'Failed to find manifest folder at {GlobalSettingsModelSingleton.get().discovery.manifests_folder_path}',
            DiscoveryEvent())
        # raise ManifestFolderNotFoundException(manifests_folder_path)

    # Verify manifest file path
    for pack in GlobalSettingsModelSingleton.get().selectors.packs:
        pack: SelectorsSettings.SelectorsPackSettings = pack
        try:
            pack.manifest_file_paths = [get_manifest_relative_path(manifests_folder_path, include_path) for include_path
                                        in pack.manifest_file_paths]
        except ManifestIdNotFoundException as e:
            logger.error('Some Configurations are wrong in the file', DiscoveryEvent())
            # raise ConfigurationFileException(config_file_path=CONFIGURATION_FILE_PATH) from e


@app.command(help="Print CLI Version")
def version() -> None:
    typer.echo(f"the CLI is at version {__version__}")


@app.command(help="Scaffold a Sample Project Structure")
## TODO: Do a network call and git clone the example folder in the github repo instead
## TODO: Let users choose which example to clone
def scaffold(project_name: str) -> None:
    root = Path(project_name).absolute()
    if root.exists():
        raise ValueError(f'File/Folder {root} already exists!')

    root.mkdir(parents=True)
    for source in Path(__file__).parent.joinpath('scaffold_data').glob('**/*'):
        if source.is_file():
            relative_path = Path(*source.relative_to(Path(__file__).parent).parts[1:])
            dest = root.joinpath(relative_path)
            dest.parent.mkdir(exist_ok=True, parents=True)
            dest.write_bytes(source.read_bytes())
    typer.echo(f'Project {project_name} is created!')


@app.command(help=f"Compile and dump manifests as session to Path {COMPILED_FOLDER_PATH}")
def compile(
        include_manifest_file_paths: Annotated[
            Optional[List[Path]],
            include_manifest_file_paths_option,
        ] = None,

        include_tags: Annotated[
            Optional[List[str]],
            include_tags_option,
        ] = None,

        include_models: Annotated[
            Optional[List[str]],
            include_models_option,
        ] = None,

        exclude_manifest_file_paths: Annotated[
            Optional[List[Path]],
            exclude_manifest_file_paths_option,
        ] = None,

        exclude_tags: Annotated[
            Optional[List[str]],
            exclude_tags_option,
        ] = None,

        exclude_models: Annotated[
            Optional[List[str]],
            exclude_models_option,
        ] = None,

        selectors_pack_name: Annotated[
            Optional[str],
            selector_pack_name_option,
        ] = None,

        is_interactive: Annotated[
            bool,
            is_interactive_option,
        ] = False,

        env_files_pack_name: Annotated[
            str,
            env_files_pack_name_option,
        ] = None,

        ctx: Annotated[
            Optional[List[str]],
            extra_env_var_option,
        ] = None
) -> None:
    """
    Compile and output model
    Usage:
    acp compile --ctx key1=val1 --ctx key2=val2
    """
    init_cli_settings(
        include_manifest_file_paths=include_manifest_file_paths,
        include_tags=include_tags,
        include_models=include_models,
        exclude_manifest_file_paths=exclude_manifest_file_paths,
        exclude_tags=exclude_tags,
        exclude_models=exclude_models,
        is_interactive=is_interactive,
        ctx=ctx,
        selectors_pack_name=selectors_pack_name,
        env_files_pack_name=env_files_pack_name,
    )

    required_models = parse_models(
        manifests_folder_path=GlobalSettingsModelSingleton.get().discovery.manifests_folder_path,
        selectors_pack=GlobalSettingsModelSingleton.get().current_selectors_pack,
        env_files_pack=GlobalSettingsModelSingleton.get().current_env_files_pack
    )

    session_model = convert_models_to_session(required_models)
    folder_path = COMPILED_FOLDER_PATH.joinpath(session_model.id)

    # Dump individual file
    for model in required_models:
        dump_dict_to_single_yaml_file(model.model_dump(),
                                      folder_path.joinpath(model.manifest_file_path))
    # Dump Session
    dump_dict_to_single_yaml_file(session_model.model_dump(),
                                  folder_path.joinpath('session.yaml'))

    typer.echo('Session and other accessories are compiled')


@app.command(help=f"Compile, run and dump manifests as session to Path {RUN_FOLDER_PATH}")
def run(
        include_manifest_file_paths: Annotated[
            Optional[List[Path]],
            include_manifest_file_paths_option,
        ] = None,

        include_tags: Annotated[
            Optional[List[str]],
            include_tags_option,
        ] = None,

        include_models: Annotated[
            Optional[List[str]],
            include_models_option,
        ] = None,

        exclude_manifest_file_paths: Annotated[
            Optional[List[Path]],
            exclude_manifest_file_paths_option,
        ] = None,

        exclude_tags: Annotated[
            Optional[List[str]],
            exclude_tags_option,
        ] = None,

        exclude_models: Annotated[
            Optional[List[str]],
            exclude_models_option,
        ] = None,

        selectors_pack_name: Annotated[
            Optional[str],
            selector_pack_name_option,
        ] = None,

        is_interactive: Annotated[
            bool,
            is_interactive_option,
        ] = False,

        env_files_pack_name: Annotated[
            str,
            env_files_pack_name_option,
        ] = None,

        ctx: Annotated[
            Optional[List[str]],
            extra_env_var_option,
        ] = None
):
    """
    Compile, run and output model
    acp run --ctx key1=val1 --ctx key2=val2
    """
    init_cli_settings(
        include_manifest_file_paths=include_manifest_file_paths,
        include_tags=include_tags,
        include_models=include_models,
        exclude_manifest_file_paths=exclude_manifest_file_paths,
        exclude_tags=exclude_tags,
        exclude_models=exclude_models,
        is_interactive=is_interactive,
        ctx=ctx,
        selectors_pack_name=selectors_pack_name,
        env_files_pack_name=env_files_pack_name,
    )

    required_models = parse_models(
        manifests_folder_path=GlobalSettingsModelSingleton.get().discovery.manifests_folder_path,
        selectors_pack=GlobalSettingsModelSingleton.get().current_selectors_pack,
        env_files_pack=GlobalSettingsModelSingleton.get().current_env_files_pack
    )
    session_model = convert_models_to_session(required_models)
    session_model = run_session_model(session_model)

    folder_path = RUN_FOLDER_PATH.joinpath(session_model.id)

    # Dump individual file
    for model in required_models:
        dump_dict_to_single_yaml_file(model.model_dump(),
                                      folder_path.joinpath(model.manifest_file_path))

    dump_dict_to_single_yaml_file(session_model.model_dump(),
                                  folder_path.joinpath('session.yaml'))

    if session_model.is_success:
        typer.echo('Session is completed with success')
    else:
        typer.echo('Session is completed with error')
        raise typer.Exit(1)


@app.command(help=f""" Clean all output folders. All of {[str(path) for path in OUTPUT_PATHS]}  """)
def clean(
):
    paths_to_clean: List[Path] = [
        GlobalSettingsModelSingleton.get().run_folder,
        GlobalSettingsModelSingleton.get().compiled_folder,
        GlobalSettingsModelSingleton.get().reporting.reports_folder,
        GlobalSettingsModelSingleton.get().logging.log_file_path
    ]

    for path_to_clean in paths_to_clean:
        logger.info(f'Cleaning Path {path_to_clean}...')
        if path_to_clean.is_file():
            path_to_clean.unlink()

        if path_to_clean.is_dir():
            shutil.rmtree(path_to_clean)
