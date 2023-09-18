from abc import ABC, abstractmethod
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class BaseSerde(ABC):
    default_deserialised: Any

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    @classmethod
    @abstractmethod
    def deserialise(cls, text: str) -> Any:
        pass

    @classmethod
    @abstractmethod
    def serialise(cls, obj: Any) -> str:
        pass
