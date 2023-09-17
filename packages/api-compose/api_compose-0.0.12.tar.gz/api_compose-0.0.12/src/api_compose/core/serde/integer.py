import traceback

from api_compose.core.logging import get_logger
from api_compose.core.serde.base import BaseSerde

logger = get_logger(__name__)


class IntegerSerde(BaseSerde):
    default_deserialised: int = -1

    @classmethod
    def deserialise(cls, text: str) -> int:
        try:
            return int(text)
        except ValueError as e:
            logger.error(traceback.format_exc())
            return cls.default_deserialised

    @classmethod
    def serialise(cls, integer: int) -> str:
        return str(integer)
