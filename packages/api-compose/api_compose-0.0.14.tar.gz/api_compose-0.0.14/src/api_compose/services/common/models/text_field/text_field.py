from enum import Enum
from typing import Any, Union, Optional, Literal

from pydantic import BaseModel as _BaseModel, Field
from pydantic import field_serializer

from api_compose.core.logging import get_logger
from api_compose.core.serde.base import BaseSerde
from api_compose.core.serde.integer import IntegerSerde
from api_compose.core.serde.json import JsonSerde
from api_compose.core.serde.str import StringSerde
from api_compose.core.serde.xml import XmlSerde
from api_compose.core.serde.yaml import YamlSerde
from api_compose.services.common.events.text_field import TextFieldEvent
from api_compose.services.common.models.text_field.exceptions import TextDeserialisationFailureException

logger = get_logger(__name__)


class TextFieldFormatEnum(str, Enum):
    STRING = 'string'
    INTEGER = 'integer'
    YAML = 'yaml'
    JSON = 'json'
    XML = 'xml'


class BaseTextField(_BaseModel):
    format: TextFieldFormatEnum
    serde: BaseSerde = Field(exclude=True)

    @field_serializer('serde')
    def serialize_serde(self, serde: BaseSerde, _info):
        return serde.__str__()

    # Other properties
    text: Optional[str] = Field(None)
    obj: Optional[Any] = Field(None)

    # Setters

    def deserialise_to_obj(self):
        try:
            self.obj = self.serde.deserialise(self.text)
            logger.debug(f"deserialised to {self.obj=}")
        except Exception as e:
            logger.error(f"Error deserialising text to {self.format=} \n"
                         f"{self.text=}", TextFieldEvent())
            raise TextDeserialisationFailureException(text=self.text, format=self.format) from e

        return self


class StringTextField(BaseTextField):
    format: Literal[TextFieldFormatEnum.STRING] = TextFieldFormatEnum.STRING

    serde: StringSerde = Field(
        StringSerde(),
        exclude=True
    )


class IntegerTextField(BaseTextField):
    format: Literal[TextFieldFormatEnum.INTEGER] = TextFieldFormatEnum.INTEGER

    serde: IntegerSerde = Field(
        IntegerSerde(),
        exclude=True
    )


class YamlTextField(BaseTextField):
    format: Literal[TextFieldFormatEnum.YAML] = TextFieldFormatEnum.YAML

    serde: YamlSerde = Field(
        YamlSerde(),
        exclude=True
    )


class JsonTextField(BaseTextField):
    format: Literal[TextFieldFormatEnum.JSON] = TextFieldFormatEnum.JSON

    serde: JsonSerde = Field(
        JsonSerde(),
        exclude=True
    )


class XmlTextField(BaseTextField):
    format: Literal[TextFieldFormatEnum.XML] = TextFieldFormatEnum.XML
    serde: XmlSerde = Field(
        XmlSerde(),
        exclude=True,
    )


JsonLikeTextField = Union[JsonTextField, YamlTextField]
