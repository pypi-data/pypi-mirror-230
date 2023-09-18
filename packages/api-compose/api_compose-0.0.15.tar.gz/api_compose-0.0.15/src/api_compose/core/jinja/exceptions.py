from pathlib import Path
from typing import List, Dict, Any, Optional

from api_compose.core.utils.string import convert_keys_in_nested_dict_to_dotted_paths


class TemplateNotFoundByPathException(Exception):
    def __init__(self,
                 template_search_paths: List[Path],
                 required_template_path: str,
                 available_template_paths: List[Path],
                 ):
        self.template_search_paths = template_search_paths
        self.required_template_path = required_template_path
        self.available_template_paths = available_template_paths

    def __str__(self):
        return (f'Search Paths: {self.template_search_paths} \n'
                f'Cannot find template {self.required_template_path}. \n'
                f'Available Templates {self.available_template_paths}. \n')


class TemplateRenderFailureException(Exception):
    def __init__(
            self,
            template: str,
            exec: Exception,
            jinja_globals: Dict[str, Any],
            file_path: Optional[str] = None,
    ):
        self.template = template
        self.exec = exec
        self.jinja_globals = jinja_globals
        self.file_path = file_path

    def __str__(self):
        return f'Cannot render template {self.template=}. \n' \
               f'File Path: {str(self.file_path)} \n' \
               f'Exception Message: {str(self.exec)} \n' \
               f'Available Globals {convert_keys_in_nested_dict_to_dotted_paths(self.jinja_globals)}. \n'
