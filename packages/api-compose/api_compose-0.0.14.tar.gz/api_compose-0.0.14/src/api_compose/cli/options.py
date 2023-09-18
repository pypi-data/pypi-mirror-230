""" Typer Options """
import typer

from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.services.common.registry.processor_registry import ProcessorRegistry

env_files_pack_name_option = typer.Option("--env", "-e",
                                          help=f"Env Files Pack Name to use. One of {[pack.name for pack in GlobalSettingsModelSingleton.get().env_files.packs]}")

include_manifest_file_paths_option = typer.Option("--file", "-f",
                                                  help=f'Relative Path to Manifests to include. Relative to path {GlobalSettingsModelSingleton.get().discovery.manifests_folder_path.absolute()}')
include_tags_option = typer.Option("--tag", "-t", help="Tag in manifest to look for to include")
include_models_option = typer.Option("--model", "-m",
                                     help=f"Models to include. One of {[name for name in ProcessorRegistry.get_available_model_names()]}")

exclude_manifest_file_paths_option = typer.Option("--no-file", "-F",
                                                  help=f'Relative Path to Manifests to exclude. Relative to path {GlobalSettingsModelSingleton.get().discovery.manifests_folder_path.absolute()}')
exclude_tags_option = typer.Option("--no-tag", "-T", help="Tag in manifest to look for to exclude")
exclude_models_option = typer.Option("--no-model", "-M",
                                     help=f"Models to exclude. One of {[name for name in ProcessorRegistry.get_available_model_names()]}")

selector_pack_name_option = typer.Option("--selector", "-s",
                                         help=f"Selectors Pack name to use. One of {[pack.name for pack in GlobalSettingsModelSingleton.get().selectors.packs]}")

is_interactive_option = typer.Option("--interactive/--no-interactive", "-i/-I", help='Start interactive shell or not')
extra_env_var_option = typer.Option()
