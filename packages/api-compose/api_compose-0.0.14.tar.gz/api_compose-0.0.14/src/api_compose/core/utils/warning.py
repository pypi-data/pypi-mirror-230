from typing import Callable

from api_compose.core.logging import get_logger

logger = get_logger(__name__)

def warning(message:str):
    def inner(func: Callable):
        def wrapper(*args, **kwargs):
            # Log warning only when the decorated method is executed
            logger.warning(message)
            return func(*args, **kwargs)
        return wrapper

    return inner