import traceback
from typing import Any, Dict, Union, List

import yaml

from api_compose.core.logging import get_logger
from api_compose.core.serde.base import BaseSerde

logger = get_logger(__name__)


class YamlSerde(BaseSerde):
    default_deserialised: Dict = {}

    @classmethod
    def deserialise(cls, text: str) -> Union[Dict, List]:
        try:
            output = yaml.load(text, Loader=yaml.Loader)
        except AttributeError as e:
            logger.error(traceback.format_exc())
            output = cls.default_deserialised
        else:
            # Check empty string or NoneType
            if not output:
                output = cls.default_deserialised
        return output


    @classmethod
    def serialise(cls, obj: Union[Dict, List]) -> str:
        return yaml.dump(obj)
