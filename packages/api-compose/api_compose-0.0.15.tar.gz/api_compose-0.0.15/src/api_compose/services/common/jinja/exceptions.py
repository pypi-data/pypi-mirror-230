from typing import List

from api_compose.services.common.registry.jinja_function_registry import FunctionModel


class JinjaFunctionNamespaceClashException(Exception):

    def __init__(
            self,
            jinja_function_models: List[FunctionModel]
    ):
        self.jinja_function_models = jinja_function_models

    def __str__(self):
        return f"""There's a name or namespace clash of the below jinja functions:
         {[model.name for model in self.jinja_function_models]}
         Please correct the names the jinja functions
         """
