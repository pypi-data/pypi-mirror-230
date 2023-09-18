from typing import Union, List, Any

from lxml import etree


def parse_xml_with_xpath(
        xml_doc: etree.ElementBase,
        xpath: str,
        get_all_matches=False
) -> Union[List, Any]:
    result: List[Any] = xml_doc.xpath(xpath)

    if get_all_matches:
        return result
    else:
        return result[0]
