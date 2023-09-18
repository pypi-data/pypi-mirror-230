import traceback

from api_compose.core.logging import get_logger
from api_compose.core.serde.base import BaseSerde

logger = get_logger(__name__)


class StringSerde(BaseSerde):
    default_deserialised: str = ''

    @classmethod
    def deserialise(cls, text: str) -> str:
        try:
            return str(text)
        except Exception as e:
            logger.error(traceback.format_exc())
            return cls.default_deserialised

    @classmethod
    def serialise(cls, obj: str) -> str:
        return str(obj)
