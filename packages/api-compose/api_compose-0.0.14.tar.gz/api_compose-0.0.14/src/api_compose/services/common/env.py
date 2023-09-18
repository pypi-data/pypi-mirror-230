from pathlib import Path
from typing import Any, Dict, List

import yaml
from yaml.parser import ParserError

from api_compose.core.jinja.core.context import BaseJinjaContext
from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.core.jinja.exceptions import TemplateRenderFailureException
from api_compose.core.utils.dict import merge_dict
from api_compose.services.common.jinja import build_env_file_jinja_engine
from api_compose.services.common.models.text_field.exceptions import TextDeserialisationFailureException


def get_env_vars_context(
        yaml_file_paths: List[Path]
) -> Dict[str, Any]:
    return render_load_and_merge_templated_yamls_as_single_dict(
        yaml_file_paths=yaml_file_paths,
        jinja_engine=build_env_file_jinja_engine()
    )


def render_load_and_merge_templated_yamls_as_single_dict(
        yaml_file_paths: List[Path],
        jinja_engine: JinjaEngine,
) -> Dict[str, Any]:
    """Read Yamls, Render them, Merge them, return"""
    dict_ = {}
    for yaml_file_path in yaml_file_paths:
        if yaml_file_path.exists():
            with open(yaml_file_path, 'r') as f:
                template: str = f.read()
                rendered_str, is_success, exec = jinja_engine.set_template_by_string(
                    template).render_to_str(
                    BaseJinjaContext(
                        template=template
                    )
                )
                if not is_success:
                    raise TemplateRenderFailureException(
                        template=template,
                        exec=exec,
                        jinja_globals=jinja_engine._environment.globals,
                        file_path=str(yaml_file_path.absolute()),
                    ) from exec

            try:
                new_dict = yaml.load(rendered_str, Loader=yaml.FullLoader)
            except ParserError as e:
                raise TextDeserialisationFailureException(
                    text=rendered_str,
                    format='yaml',
                    file_path=str(yaml_file_path.absolute()),
                ) from e

        else:
            raise ValueError(f'Path {yaml_file_path.absolute()} does not exist!')
        # Merge
        dict_ = merge_dict(dict_, new_dict)
    return dict_
