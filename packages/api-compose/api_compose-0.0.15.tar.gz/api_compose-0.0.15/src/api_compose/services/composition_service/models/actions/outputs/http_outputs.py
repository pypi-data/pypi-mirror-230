import warnings as w
from typing import Dict, Union, List

from api_compose.core.lxml.parser import PrintableElementAnnotation, get_default_element

w.filterwarnings('ignore', module='pydantic')  # Warning of lxml.etree.E.default() as default in model

from pydantic import Field, ConfigDict

from api_compose.services.composition_service.models.actions.outputs.base_outputs import BaseActionOutputModel


class BaseHttpActionOutputModel(BaseActionOutputModel):
    url: str = Field(
        "",
        description="URL",
    )
    headers: Dict = Field(
        {},
        description="headers",
    )


class JsonHttpActionOutputModel(BaseHttpActionOutputModel):
    body: Union[List, Dict] = Field(
        {},
        description="body",
    )


class XmlHttpActionOutputModel(BaseHttpActionOutputModel):
    # FIXME
    model_config = ConfigDict(arbitrary_types_allowed=True)

    body: PrintableElementAnnotation = Field(
        get_default_element(),
        description="body",
    )


w.filterwarnings('default')  # Reset
