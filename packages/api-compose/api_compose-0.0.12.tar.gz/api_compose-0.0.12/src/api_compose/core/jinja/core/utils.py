__all__ = ['extract_from_template_str']

import re
from typing import List

from api_compose.core.logging import get_logger

logger = get_logger(name=__name__)


def extract_from_template_str(templ_str: str) -> List:
    rgx = re.compile("{{(?P<name>[^{}]+)}}")
    variable_names = {match.group("name").strip() for match in rgx.finditer(templ_str)}
    return list(variable_names)


