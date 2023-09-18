from api_compose import get_logger
from api_compose import FunctionsRegistry

logger = get_logger(name=__name__)


@FunctionsRegistry.set(name='get_one')
def return_value_one() -> int:
    return 1

