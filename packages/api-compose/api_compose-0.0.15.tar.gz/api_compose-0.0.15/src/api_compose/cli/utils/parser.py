import json
from typing import Optional, List, Dict, Tuple, Union

from api_compose.core.logging import get_logger
from api_compose.core.utils.dict import merge_dict
from api_compose.core.utils.string import convert_dotted_string_to_nested_dict
from api_compose.services.common.events.deserialisation import DeserialisationEvent

logger = get_logger(__name__)


def parse_context(context: Optional[List[str]]) -> Dict[str, Union[str, int, float, bool]]:
    base_dict = {}
    if context is not None and type(context) == list:
        pairs = []
        for kv_pair in context:
            key, val = validate_context_kv_pair(kv_pair)
            pairs.append((key, convert_string(val)))
        overlaying_dict = convert_dotted_string_to_nested_dict(pairs)
        base_dict = merge_dict(base_dict, overlaying_dict)
        logger.info('Parsed CLI context', DeserialisationEvent())
        logger.info(json.dumps(base_dict, indent=4), DeserialisationEvent())
    else:
        logger.warning('Cannot parse CLI context as it is not a list a strings \n' f'{context=}',
                       DeserialisationEvent())

    return base_dict


def convert_string(string: Optional[str]) -> Union[None, int, float, bool, str]:
    if string is not None:
        try:
            # Try converting to an integer
            result = int(string)
            return result
        except ValueError:
            try:
                # Try converting to a float
                result = float(string)
                return result
            except ValueError:
                if string.lower() == 'true':
                    # Convert to boolean - True
                    return True
                elif string.lower() == 'false':
                    # Convert to boolean - False
                    return False
                else:
                    # Return the string itself if all conversion attempts fail
                    return string
    else:
        return string


def validate_context_kv_pair(kv_pair: str) -> Tuple[str, str]:
    kv_pair = kv_pair.strip()
    assert '=' in kv_pair, f'{kv_pair} does not follow the syntax key=kv_pairue pair.'
    parts = kv_pair.split('=')
    if len(parts) > 2:
        raise ValueError(f'{kv_pair} does not follow the syntax key=kv_pairue pair.')
    key, val = parts
    return key.strip(), val.strip()
