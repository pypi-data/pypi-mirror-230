__all__ = ['Action']

import json

from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.core.logging import (get_logger)
from api_compose.services.common.models.ref_resolver import RefResolverModel
from api_compose.services.common.models.text_field.templated_text_field import StringTemplatedTextField, \
    JsonTemplatedTextField, IntegerTemplatedTextField, XmlTemplatedTextField
from api_compose.services.common.processors.base import BaseProcessor
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.composition_service.jinja.context import ActionJinjaContext
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel
from api_compose.services.composition_service.models.actions.actions.dummy_action import DummyActionModel
from api_compose.services.composition_service.models.actions.actions.http_actions import JsonHttpActionModel, \
    XmlHttpActionModel
from api_compose.services.composition_service.models.actions.actions.websocket_actions import \
    JsonRpcWebSocketActionModel
from api_compose.services.composition_service.models.actions.configs.dummy_configs import DummyActionConfigModel
from api_compose.services.composition_service.models.actions.configs.http_configs import JsonHttpActionConfigModel, \
    XmlHttpActionConfigModel
from api_compose.services.composition_service.models.actions.configs.websocket_configs import \
    JsonRpcWebSocketActionConfigModel
from api_compose.services.composition_service.processors.adapters.base_adapter import BaseAdapter
from api_compose.services.composition_service.processors.schema_validators.base_schema_validator import \
    BaseSchemaValidator
from api_compose.services.persistence_service.processors.base_backend import BaseBackend

logger = get_logger(__name__)


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.Action,
    models=[
        DummyActionModel(
            model_name='DummyActionModel',
            id='example_dummy_action',
            description='Dummy Action',
            execution_id='example_dummy_action',
            config=DummyActionConfigModel(
                sleep_seconds=IntegerTemplatedTextField(template='2'),
            ),
        ),
        XmlHttpActionModel(
            model_name='XmlHttpActionModel',
            id='example_xml_http_action',
            description='Get request against http://httpbin.org/get',
            execution_id='example_xml_http_action',
            config=XmlHttpActionConfigModel(
                url=StringTemplatedTextField(template='https://random-data-api.com/api/users/random_user'),
                method=StringTemplatedTextField(template='GET'),
                headers=JsonTemplatedTextField(template='{}'),
                body=XmlTemplatedTextField(template=''),
                params=JsonTemplatedTextField(template=json.dumps({'is_xml': True})),
            ),
        ),
        JsonHttpActionModel(
            model_name='JsonHttpActionModel',
            id='example_json_http_action',
            description='Get request against http://httpbin.org/get',
            execution_id='example_json_http_action',
            config=JsonHttpActionConfigModel(
                url=StringTemplatedTextField(template='http://httpbin.org/get'),
                method=StringTemplatedTextField(template='GET'),
                headers=JsonTemplatedTextField(template='{}'),
                body=JsonTemplatedTextField(template='{}'),
                params=JsonTemplatedTextField(template='{}'),
            ),
        ),
        JsonRpcWebSocketActionModel(
            model_name='JsonRpcWebSocketActionModel',
            id='example_websocket_action',
            description='Postman public Websocket',
            execution_id='example_websocket_action',
            config=JsonRpcWebSocketActionConfigModel(
                url=StringTemplatedTextField(template='wss://ws.postman-echo.com/raw/query-params?key=template')
            ),
        ),

        RefResolverModel(
            model_name='RefResolverModel',
            id='some_ref',
            description='',
            ref='actions/action_one.yaml',
            context=dict(
                execution_id='action_one_exec_one',
                url='http://abc.com',
                limit='12',
            ),
        ),

    ]
)
class Action(BaseProcessor):
    """
    Action
    """

    def __init__(
            self,
            action_model: BaseActionModel,
            backend: BaseBackend,
            jinja_engine: JinjaEngine,
    ):
        super().__init__()
        self.adapter: BaseAdapter = ProcessorRegistry.create_processor_by_name(
            class_name=action_model.adapter_class_name,
            config={
                **dict(action_model=action_model, jinja_engine=jinja_engine, )
            }
        )
        self.backend = backend
        self.action_model = action_model

    def start(self, jinja_context: ActionJinjaContext):
        self.adapter.start(jinja_context)

    def stop(self):
        self.adapter.stop()
        self.backend.add(self.action_model)

    def validate_schema(self):
        for schema_validator_model in self.action_model.schema_validators:
            self.schema_validator: BaseSchemaValidator = ProcessorRegistry.create_processor_by_name(
                class_name=schema_validator_model.class_name,
                config={'schema_models': self.action_model.schemas,
                        'action_output_model': self.action_model.output,
                        'schema_validator_model': schema_validator_model,
                        }
            )

            self.schema_validator.validate()

    @property
    def state(self):
        return self.action_model.state

    @property
    def execution_id(self):
        return self.action_model.execution_id
