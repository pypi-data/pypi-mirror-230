from typing import Union, List, Dict, Any

import lxml.etree

from api_compose import FunctionsRegistry, FunctionType
from api_compose.core.utils.json_path import parse_json_with_jsonpath
from api_compose.core.utils.xpath import parse_xml_with_xpath


@FunctionsRegistry.set(
    name='acp.paths.jpath',
    func_type=FunctionType.JinjaFilter,
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



@FunctionsRegistry.set(
    name='acp.paths.xpath',
    func_type=FunctionType.JinjaFilter,
    alias=['xpath'],
)
def filter_by_json_path(
        xml_doc: lxml.etree.ElementBase,
        xpath: str,
        get_all_matches: bool = False,
):
    """
    """
    if xpath:
        return parse_xml_with_xpath(xml_doc, xpath, get_all_matches)
    else:
        return xml_doc
