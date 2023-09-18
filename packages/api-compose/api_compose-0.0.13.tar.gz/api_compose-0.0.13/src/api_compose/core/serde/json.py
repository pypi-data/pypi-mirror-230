import json
import traceback
from json import JSONDecodeError
from typing import Union, Dict, List

from api_compose.core.logging import get_logger
from api_compose.core.serde.base import BaseSerde

logger = get_logger(__name__)


class JsonSerde(BaseSerde):
    default_deserialised: Dict = {}

    @classmethod
    def deserialise(cls, text: str) -> Union[Dict, List]:
        try:
            return json.loads(text)
        except JSONDecodeError as e:
            logger.error(traceback.format_exc())
            return cls.default_deserialised

    @classmethod
    def serialise(cls, obj: Union[Dict, List]) -> str:
        return json.dumps(obj)
