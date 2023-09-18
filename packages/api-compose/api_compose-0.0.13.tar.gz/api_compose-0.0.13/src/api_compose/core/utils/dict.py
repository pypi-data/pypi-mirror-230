from typing import Dict, Tuple, List, Union, Any


def count_items(item: Union[Dict, List, Tuple, Any]) -> int:
    """
    Count the number of items in nested dict, nested list or nested tuple. All other data types count as one.
    Parameters
    ----------
    item

    Returns
    -------

    """
    count = 0

    if isinstance(item, dict):
        for value in item.values():
            count += count_items(value)  # Recursively count items in nested dictionaries
    elif isinstance(item, list) or isinstance(item, tuple):
        for i in item:
            count += count_items(i)
    else:
        count += 1  # Count individual items

    return count


def merge_dict(overlayed_dict: Dict[str, Any], overlaying_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Overlay the `overlaying_dict` on top of the `overlayed_dict`, and include fields missing from the `overlayed_dict`
    """
    new_dict = overlayed_dict.copy()
    for key, value in overlaying_dict.items():
        if key in overlayed_dict:
            # If the key is present in both dictionaries and its value is a dictionary,
            # recursively call overlay_dict() on the value
            if isinstance(value, dict) and isinstance(new_dict[key], dict):
                new_dict[key] = merge_dict(new_dict[key], value)
            else:
                new_dict[key] = value
        else:
            new_dict[key] = value

    return new_dict
