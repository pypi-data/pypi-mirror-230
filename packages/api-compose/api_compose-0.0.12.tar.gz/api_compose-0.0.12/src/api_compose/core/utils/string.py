import re
import string
from typing import List, Iterable, Tuple, Any, Dict

from api_compose.core.logging import (get_logger)

logger = get_logger(__name__)


def split_pascal_case_string(s: str) -> List[str]:
    result = []
    current_word = s[0]

    for i in range(1, len(s)):
        if s[i].isupper():
            result.append(current_word)
            current_word = s[i]
        else:
            current_word += s[i]

    result.append(current_word)
    return result


def convert_keys_in_nested_dict_to_dotted_paths(dictionary, parent_key='', sep='.') \
        -> List[str]:
    """
    Recursively retrieves a list of dotted paths from a nested dictionary.

    Args:
        dictionary (dict): The nested dictionary.
        parent_key (str): The parent key to use for the dotted path.
        sep (str): The separator to use between keys in the dotted path.

    Returns:
        list: A list of dotted paths.
    """
    dotted_paths = []

    if not isinstance(dictionary, dict):
        return dotted_paths

    for key, value in dictionary.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            dotted_paths.extend(convert_keys_in_nested_dict_to_dotted_paths(value, new_key, sep=sep))
        else:
            dotted_paths.append(new_key)
    return dotted_paths


def convert_dotted_string_to_nested_dict(pairs: Iterable[Tuple[str, Any]]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    pairs Iterable of string (in dots) - anything pairs
    Returns
    -------

    """
    nested_dict = {}

    for key, value in pairs:
        keys = key.split('.')
        current_dict = nested_dict

        for i, key in enumerate(keys):
            if type(current_dict) != dict:
                logger.error(
                    f'Cannot create nested dict for key path **{keys}** as it is already occupied by **{current_dict}**')
                current_dict = {}

            if i == len(keys) - 1:
                current_dict[key] = value
            else:
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]

    return nested_dict


def normalise_sentence(sentence: str) -> str:
    """
    Parameters
    ----------
    sentence

    Returns
    -------
    """
    return re.sub('\s+', ' ', (sentence.lower().translate(str.maketrans('', '', string.punctuation))).strip())
