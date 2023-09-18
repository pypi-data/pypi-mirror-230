from typing import Annotated
from xml.etree.ElementTree import XMLParser

from lxml import etree
from lxml.etree import ElementBase
from pydantic import PlainSerializer


class PrintableElement(etree.ElementBase):
    def __str__(self):
        return etree.tostring(self).decode('utf-8')

    def __repr__(self):
        return etree.tostring(self).decode('utf-8')


def get_parser() -> XMLParser:
    parser_lookup = etree.ElementDefaultClassLookup(element=PrintableElement)
    parser = etree.XMLParser()
    parser.set_element_class_lookup(parser_lookup)
    return parser


def get_default_element() -> ElementBase:
    return etree.fromstring(
        b'<?xml version="1.0" encoding="UTF-8"?><default> </default>',
        parser=get_parser())


def get_default_schema() -> ElementBase:
    return etree.fromstring(
        b'''<?xml version="1.0" encoding="UTF-8"?><xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"> <xs:element name="default"> <xs:complexType> <xs:simpleContent> <xs:extension base="xs:string"> <xs:attribute name="version" type="xs:string" /> </xs:extension> </xs:simpleContent> </xs:complexType> </xs:element> </xs:schema>''',
        parser=get_parser())


# To be used in Pydantic Model for serialisation
PrintableElementAnnotation = Annotated[
    PrintableElement,
    # Keep the html tags when json dumped
    PlainSerializer(lambda x: etree.tostring(x, pretty_print=True).decode('utf-8'), return_type=str, when_used='json')
]
