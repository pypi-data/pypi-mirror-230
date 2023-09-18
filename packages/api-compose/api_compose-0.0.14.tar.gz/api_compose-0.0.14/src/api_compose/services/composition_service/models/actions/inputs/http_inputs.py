import warnings as w
from typing import Dict

from api_compose.core.lxml.parser import PrintableElementAnnotation, get_default_element

w.filterwarnings('ignore', module='pydantic')  # Warning of lxml.etree.E.default() as default in model

from pydantic import Field, ConfigDict

from api_compose.services.composition_service.models.actions.inputs.base_inputs import BaseActionInputModel


class BaseHttpActionInputModel(BaseActionInputModel):
    url: str = Field(
        "",
        description='URL',
    )
    method: str = Field(
        '',
        description="HTTP Method",
    )
    headers: Dict = Field(
        {},
        description='HTTP Header',
    )
    params: Dict = Field(
        {},
        description='HTTP URL params',
    )


class JsonHttpActionInputModel(BaseHttpActionInputModel):
    body: Dict = Field(
        {},
        description='HTTP body',
    )


class XmlHttpActionInputModel(BaseHttpActionInputModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    body: PrintableElementAnnotation = Field(
        get_default_element(),
        description='HTTP body',
    )


w.filterwarnings('default')  # Reset
