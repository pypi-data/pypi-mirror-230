from typing import Union, List, Literal

from pydantic import Field

from api_compose.core.logging import get_logger
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel
from api_compose.services.composition_service.models.actions.actions.http_actions import BaseHttpActionModel
from api_compose.services.composition_service.models.actions.configs.websocket_configs import \
    JsonRpcWebSocketActionConfigModel
from api_compose.services.composition_service.models.actions.inputs.websocket_inputs import \
    JsonRpcWebSocketActionInputModel
from api_compose.services.composition_service.models.actions.outputs.websocket_outputs import \
    JsonRpcWebSocketActionOutputModel
from api_compose.services.composition_service.models.actions.schemas import JsonSchemaModel
from api_compose.services.composition_service.models.protocols.status_enums import WebSocketResponseStatusEnum, \
    OtherResponseStatusEnum
from api_compose.services.composition_service.models.schema_validatiors.schema_validators import \
    JsonSchemaValidatorModel

logger = get_logger(__name__)


class JsonRpcWebSocketActionModel(BaseHttpActionModel):
    model_name: Literal['JsonRpcWebSocketActionModel'] = Field(
        description=BaseActionModel.model_fields['model_name'].description
    )

    adapter_class_name: str = Field(
        'JsonRpcWebsocketAdapter',
        description=BaseHttpActionModel.model_fields['adapter_class_name'].description,
    )

    config: JsonRpcWebSocketActionConfigModel = Field(
        JsonRpcWebSocketActionConfigModel(),
        description=BaseHttpActionModel.model_fields['config'].description,

    )

    input: JsonRpcWebSocketActionInputModel = Field(
        JsonRpcWebSocketActionInputModel(),
        description=BaseHttpActionModel.model_fields['input'].description,
    )
    output: JsonRpcWebSocketActionOutputModel = Field(
        JsonRpcWebSocketActionOutputModel(),
        description=BaseHttpActionModel.model_fields['output'].description,
    )
    response_status: Union[WebSocketResponseStatusEnum, OtherResponseStatusEnum] = Field(
        OtherResponseStatusEnum.UNITIALISED_STATUS,
        description=BaseHttpActionModel.model_fields['response_status'].description,
    )

    schemas: List[JsonSchemaModel] = Field(
        [],
        description=BaseHttpActionModel.model_fields['schemas'].description,
    )

    schema_validators: List[JsonSchemaValidatorModel] = Field(
        [],
        description=BaseHttpActionModel.model_fields['schema_validators'].description,
    )
