from typing import List


def get_duplicates_in_list(
        list_: List
) -> List:
    """Return Duplicate items in a given list."""
    visited = set()
    return list(set([x for x in list_ if x in visited or (visited.add(x) or False)]))
