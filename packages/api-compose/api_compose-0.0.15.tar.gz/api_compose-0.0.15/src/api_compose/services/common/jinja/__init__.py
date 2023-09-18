__all__ = ['build_compile_time_jinja_engine', 'build_runtime_jinja_engine']

from pathlib import Path
from typing import Tuple, Dict

from jinja2 import StrictUndefined

from api_compose.core.jinja.core.engine import JinjaEngine, JinjaTemplateSyntax
from api_compose.core.utils.dict import count_items
from api_compose.core.utils.files import is_folder_populated, are_files_unique_in
from api_compose.core.utils.string import convert_dotted_string_to_nested_dict
from api_compose.services.common.exceptions import ManifestFolderEmptyException, ManifestIdNonUniqueException
from api_compose.services.common.jinja.exceptions import JinjaFunctionNamespaceClashException
from .actions import *
from .tests import *
from .utils import *
from .paths import *


def get_jinja_functions() -> Tuple[Dict, Dict, Dict]:
    globals = convert_dotted_string_to_nested_dict(
        [(name, model.func) for model in FunctionsRegistry.registry
         for name in model.all_names if model.func_type == FunctionType.JinjaGlobal])

    filters = {name: model.func for model in FunctionsRegistry.registry if model.func_type == FunctionType.JinjaFilter
               for name in model.all_names}
    tests = {name: model.func for model in FunctionsRegistry.registry if model.func_type == FunctionType.JinjaTest for
             name in model.all_names}

    if count_items(globals) + count_items(filters) + count_items(tests) != len([name for entry in FunctionsRegistry.registry for name in entry.all_names]):
        raise JinjaFunctionNamespaceClashException(FunctionsRegistry.registry)

    return globals, filters, tests

def build_env_file_jinja_engine():
    globals, filters, tests = get_jinja_functions()

    return JinjaEngine(
        undefined=StrictUndefined,
        jinja_template_syntax=JinjaTemplateSyntax.SQUARE_BRACKETS,
        globals=globals,
        filters=filters,
        tests=tests,
    )


def build_compile_time_jinja_engine(
        manifests_folder_path: Path,
) -> JinjaEngine:
    globals, filters, tests = get_jinja_functions()

    if not is_folder_populated(manifests_folder_path):
        raise ManifestFolderEmptyException(manifests_folder_path)

    if not are_files_unique_in(manifests_folder_path):
        raise ManifestIdNonUniqueException(manifests_folder_path)

    return JinjaEngine(
        undefined=StrictUndefined,
        jinja_template_syntax=JinjaTemplateSyntax.SQUARE_BRACKETS,
        templates_search_paths=[
            manifests_folder_path,
        ],
        globals=globals,
        filters=filters,
        tests=tests,
    )


def build_runtime_jinja_engine(
) -> JinjaEngine:
    globals, filters, tests = get_jinja_functions()

    return JinjaEngine(
        globals=globals,
        filters=filters,
        tests=tests,
        jinja_template_syntax=JinjaTemplateSyntax.CURLY_BRACES,
    )
