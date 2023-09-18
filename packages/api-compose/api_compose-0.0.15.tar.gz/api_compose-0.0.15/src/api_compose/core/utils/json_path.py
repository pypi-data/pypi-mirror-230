from typing import Union, Dict, List, Any

from jsonpath_ng.ext import parse

from api_compose.core.utils.exceptions import NoMatchesFoundForJsonPathException


def parse_json_with_jsonpath(deserialised_json: Union[Dict, List, None], json_path: str, get_all_matches=False) -> \
        Union[Any, List[Any]]:
    """

    Parameters
    ----------
    deserialised_json
    json_path
    get_all_matches: whether to get all matches after applying json_path. If False, only get first match

    Returns
    -------

    """
    if deserialised_json is None:
        raise NoMatchesFoundForJsonPathException(deserialised_json=deserialised_json, json_path=json_path)
    else:
        json_path_expr = parse(json_path)
        matches = [match.value for match in json_path_expr.find(deserialised_json)]
        if len(matches) == 0:
            raise NoMatchesFoundForJsonPathException(deserialised_json=deserialised_json, json_path=json_path)

        if get_all_matches:
            return matches
        else:
            return matches[0]
