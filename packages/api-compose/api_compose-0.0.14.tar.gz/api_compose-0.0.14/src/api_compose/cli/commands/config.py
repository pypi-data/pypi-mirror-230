"""
config subcommand
"""
from pathlib import Path

import typer

from api_compose import GlobalSettingsModelSingleton
from api_compose.cli.utils.yaml_dumper import dump_dict_to_single_yaml_file

app = typer.Typer(
    help="Configure your programme",
    no_args_is_help=True
)


@app.command(help="Initialise Configuration File")
def init() -> None:
    """
    generate a config file

    :return:
    """
    config_file = Path('config.yaml')
    if config_file.exists():
        typer.echo(f'Config File {config_file.absolute()} already exists! Aborted')
    else:
        # Get config
        dump_dict_to_single_yaml_file(
            GlobalSettingsModelSingleton.get().model_dump(
                exclude={
                    'cli_options',
                    'current_env_files_pack_name',
                    'current_selectors_pack_name',
                }
            ),
            config_file
        )
        typer.echo(f'Config File {config_file.absolute()} is created')
