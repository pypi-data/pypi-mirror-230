from typing import Union, List, Annotated, Literal

from pydantic import Field

from api_compose.core.logging import get_logger
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel
from api_compose.services.composition_service.models.actions.configs.http_configs import BaseHttpActionConfigModel, \
    JsonHttpActionConfigModel, XmlHttpActionConfigModel
from api_compose.services.composition_service.models.actions.inputs.http_inputs import BaseHttpActionInputModel, \
    JsonHttpActionInputModel, XmlHttpActionInputModel
from api_compose.services.composition_service.models.actions.outputs.http_outputs import BaseHttpActionOutputModel, \
    JsonHttpActionOutputModel, XmlHttpActionOutputModel
from api_compose.services.composition_service.models.actions.schemas import JsonSchemaModel, XmlSchemaModel
from api_compose.services.composition_service.models.annotations import XmlHttpActionModelSchemaAnnotation, \
    XmlHttpActionModelSchemaValidatorAnnotation
from api_compose.services.composition_service.models.protocols.protocols import ActionAPIProtocolEnum
from api_compose.services.composition_service.models.protocols.status_enums import HttpResponseStatusEnum, \
    OtherResponseStatusEnum
from api_compose.services.composition_service.models.schema_validatiors.schema_validators import \
    JsonSchemaValidatorModel, XmlSchemaValidatorModel

logger = get_logger(__name__)


class BaseHttpActionModel(BaseActionModel):
    model_name: Literal['BaseHttpActionModel'] = Field(
        description=BaseActionModel.model_fields['model_name'].description
    )

    adapter_class_name: str = Field(
        'BaseHttpAdapter',
        description=BaseActionModel.model_fields['adapter_class_name'].description,
    )
    config: BaseHttpActionConfigModel = Field(
        BaseHttpActionConfigModel(),
        description=BaseActionModel.model_fields['config'].description,
    )
    api_protocol: ActionAPIProtocolEnum = Field(
        ActionAPIProtocolEnum.HTTP,
        description=BaseActionModel.model_fields['api_protocol'].description,
    )

    input: BaseHttpActionInputModel = Field(
        BaseHttpActionInputModel(),
        description=BaseActionModel.model_fields['input'].description,
    )
    output: BaseHttpActionOutputModel = Field(
        BaseHttpActionOutputModel(),
        description=BaseActionModel.model_fields['output'].description,
    )
    response_status: Union[HttpResponseStatusEnum, OtherResponseStatusEnum] = Field(
        OtherResponseStatusEnum.UNITIALISED_STATUS,
        description=BaseActionModel.model_fields['response_status'].description,
    )


class JsonHttpActionModel(BaseHttpActionModel):
    model_name: Literal['JsonHttpActionModel'] = Field(
        description=BaseActionModel.model_fields['model_name'].description
    )
    adapter_class_name: str = Field(
        'JsonHttpAdapter',
        description=BaseHttpActionModel.model_fields['adapter_class_name'].description,
    )
    config: JsonHttpActionConfigModel = Field(
        JsonHttpActionConfigModel(),
        description=BaseHttpActionModel.model_fields['config'].description,
    )

    input: JsonHttpActionInputModel = Field(
        JsonHttpActionInputModel(),
        description=BaseHttpActionModel.model_fields['input'].description,
    )
    output: JsonHttpActionOutputModel = Field(
        JsonHttpActionOutputModel(),
        description=BaseHttpActionModel.model_fields['output'].description,
    )

    schemas: List[JsonSchemaModel] = Field(
        [],
        description=BaseActionModel.model_fields['schemas'].description,
    )

    schema_validators: List[JsonSchemaValidatorModel] = Field(
        [],
        description=BaseActionModel.model_fields['schema_validators'].description,
        discriminator='model_name',
    )


class XmlHttpActionModel(BaseHttpActionModel):
    model_name: Literal['XmlHttpActionModel'] = Field(
        description=BaseActionModel.model_fields['model_name'].description
    )

    adapter_class_name: str = Field(
        'XmlHttpAdapter',
        description=BaseHttpActionModel.model_fields['adapter_class_name'].description,
    )

    config: XmlHttpActionConfigModel = Field(
        XmlHttpActionConfigModel(),
        description=BaseHttpActionModel.model_fields['config'].description,
    )

    input: XmlHttpActionInputModel = Field(
        XmlHttpActionInputModel(),
        description=BaseHttpActionModel.model_fields['input'].description,
    )
    output: XmlHttpActionOutputModel = Field(
        XmlHttpActionOutputModel(),
        description=BaseHttpActionModel.model_fields['output'].description,
    )

    schemas: XmlHttpActionModelSchemaAnnotation = Field(
        # XML HTTP exchange might contain both JSON (e.g. headers) and XML (e.g. body)
        [],
        description=BaseHttpActionModel.model_fields['schemas'].description,
    )

    schema_validators: XmlHttpActionModelSchemaValidatorAnnotation = Field(
        # XML HTTP exchange might contain both JSON (e.g. headers) and XML (e.g. body)
        [],
        description=BaseHttpActionModel.model_fields['schema_validators'].description,
    )


