import traceback

from lxml import etree
from lxml.etree import XMLSyntaxError

from api_compose.core.logging import get_logger
from api_compose.core.lxml.parser import PrintableElement, get_default_element
from api_compose.core.serde.base import BaseSerde

logger = get_logger(__name__)


class XmlSerde(BaseSerde):
    default_deserialised: PrintableElement = get_default_element()

    @classmethod
    def deserialise(cls, text: str) -> PrintableElement:
        try:
            return etree.fromstring(text)
        except XMLSyntaxError as e:
            logger.error(traceback.format_exc())
            return cls.default_deserialised

    @classmethod
    def serialise(cls, obj: PrintableElement) -> str:
        return etree.tostring(obj, encoding='unicode')
