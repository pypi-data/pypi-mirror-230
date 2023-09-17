## TODO: Update XML HTTP Adapter


__all__ = ["XmlHttpAdapter"]

import requests
from lxml import etree

from api_compose.core.logging import get_logger
from api_compose.core.lxml.parser import get_parser, get_default_element
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.composition_service.jinja.context import ActionJinjaContext
from api_compose.services.composition_service.models.actions.actions.http_actions import XmlHttpActionModel
from api_compose.services.composition_service.models.actions.inputs.http_inputs import XmlHttpActionInputModel
from api_compose.services.composition_service.models.actions.outputs.http_outputs import XmlHttpActionOutputModel
from api_compose.services.composition_service.processors.adapters.http_adapter.base_http_adapter import BaseHttpAdapter

logger = get_logger(name=__name__)


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.Adapter,
    models=[]
)
class XmlHttpAdapter(BaseHttpAdapter):
    """
    XML Communication over HTTP
    """

    ERROR_OUTPUT_BODY: str = '<?xml version="1.0" ?><error> </error>'

    def __init__(
            self,
            action_model: XmlHttpActionModel,
            *args,
            **kwargs,
    ):
        super().__init__(action_model, *args, **kwargs)
        self.body = action_model.config.body
        self.encoding = action_model.config.encoding

        # values to be set
        self.input: XmlHttpActionInputModel = XmlHttpActionInputModel()
        self.output: XmlHttpActionOutputModel = XmlHttpActionOutputModel()

    def _on_start(self, jinja_context: ActionJinjaContext):
        super()._on_start(jinja_context)
        self.body_obj = self.body.render_to_text(jinja_engine=self.jinja_engine,
                                                 jinja_context=self.jinja_context).deserialise_to_obj().obj
        self.encoding_obj = self.encoding.render_to_text(jinja_engine=self.jinja_engine,
                                                         jinja_context=self.jinja_context).deserialise_to_obj().obj

    def _on_exchange(self):
        super()._on_exchange()

        self.response = requests.request(
            method=self.method_obj,
            url=self.url_obj,
            headers=self.headers_obj,
            params=self.params_obj,
            data=self.body_obj if self.body_obj else None,  # noqa - will be initialised in child class
            verify=False,
        )

    def _set_input(self):
        body = etree.fromstring(self.response.request.body,
                                parser=get_parser()) if self.response.request.body is not None else get_default_element()
        self.input = XmlHttpActionInputModel(
            url=self.response.request.url,
            method=self.response.request.method,
            headers=dict(self.response.request.headers),
            params=self.params_obj,
            body=body
        )

    def _set_output(self):
        body = etree.fromstring(self.response.text.encode(self.encoding_obj), parser=get_parser())
        self.output = XmlHttpActionOutputModel(
            url=self.response.url,
            status_code=self.response.status_code,
            headers=self.response.headers,
            body=body
        )
