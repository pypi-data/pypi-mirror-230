from typing import Union, List, Dict, Any

from api_compose import JinjaFunctionsRegistry, JinjaFunctionType
from api_compose.core.utils.transformers import parse_json_with_jsonpath


@JinjaFunctionsRegistry.set(
    name='acp.paths.jpath',
    func_type=JinjaFunctionType.Filter,
    alias=['jpath'],
)
def filter_by_json_path(
        list_or_dict: Union[List, Dict],
        json_path: str,
        get_all_matches: bool = False,
):
    """
    Example Usage in Jinja: {{ dict({'abc': 12}) | acp.paths.jpath('$.abc') }}
    """
    if json_path:
        return parse_json_with_jsonpath(list_or_dict, json_path, get_all_matches)
    else:
        return list_or_dict



# @JinjaFunctionsRegistry.set(
#     name='acp.paths.xpath',
#     func_type=JinjaFunctionType.Filter,
#     alias=['xpath'],
# )
# def filter_by_json_path(
#         xml: Any,
#         xpath: str,
# ):
#     """
#     """
#     raise NotImplementedError()
