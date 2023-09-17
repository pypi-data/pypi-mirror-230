from __future__ import annotations

from lxml import etree
from pydantic import Field

from api_compose.core.lxml.parser import get_default_element
from api_compose.services.common.models.text_field.templated_text_field import StringTemplatedTextField, \
    JsonLikeTemplatedTextField, JsonTemplatedTextField, XmlTemplatedTextField
from api_compose.services.composition_service.models.actions.configs.base_configs import BaseActionConfigModel


class BaseHttpActionConfigModel(BaseActionConfigModel):
    url: StringTemplatedTextField = Field(
        StringTemplatedTextField(template=''),
        description='Templateable URL',
    )
    method: StringTemplatedTextField = Field(
        StringTemplatedTextField(template='GET'),
        description='Templateable HTTP Method',
    )
    headers: JsonLikeTemplatedTextField = Field(
        JsonTemplatedTextField(template="{}"),
        description='Templateable HTTP Headers',
    )
    params: JsonLikeTemplatedTextField = Field(
        JsonTemplatedTextField(template="{}"),
        description='Templateable HTTP Params',
    )


class JsonHttpActionConfigModel(BaseHttpActionConfigModel):
    body: JsonLikeTemplatedTextField = Field(
        JsonTemplatedTextField(template="{}"),
        description='Templateable HTTP body',
    )


class XmlHttpActionConfigModel(BaseHttpActionConfigModel):
    body: XmlTemplatedTextField = Field(
        XmlTemplatedTextField(template=etree.tostring(get_default_element())),
        description='Templateable HTTP body',
    )

    encoding: StringTemplatedTextField = Field(
        StringTemplatedTextField(template='utf-8'),
        description='Templateable encoding. Used to encode the returned XML body',
    )
