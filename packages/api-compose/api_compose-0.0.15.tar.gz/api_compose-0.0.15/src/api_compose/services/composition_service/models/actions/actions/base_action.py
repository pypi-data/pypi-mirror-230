from enum import Enum
from typing import Dict, Optional, List, Any, Literal, Union

from pydantic import Field, model_validator, field_validator

from api_compose.core.logging import get_logger
from api_compose.core.utils.exceptions import ReservedKeywordsException
from api_compose.services.common.models.base import BaseModel
from api_compose.services.composition_service.models.actions.configs.base_configs import BaseActionConfigModel
from api_compose.services.composition_service.models.actions.inputs.base_inputs import BaseActionInputModel
from api_compose.services.composition_service.models.actions.outputs.base_outputs import BaseActionOutputModel
from api_compose.services.composition_service.models.actions.schemas import BaseSchemaModel
from api_compose.services.composition_service.models.actions.states import ActionStateEnum
from api_compose.services.composition_service.models.protocols.protocols import ActionAPIProtocolEnum
from api_compose.services.composition_service.models.protocols.status_enums import OtherResponseStatusEnum
from api_compose.services.composition_service.models.schema_validatiors.schema_validators import \
    BaseSchemaValidatorModel

logger = get_logger(__name__)


class ReservedExecutionId(Enum):
    # Execution Id for the current action model
    Self = 'self'


class BaseActionModel(BaseModel):
    """
    Base Action.
    Action should follow the convention

    <MessageFormat><TransportProtocol>Action
    """
    model_name: Literal['BaseActionModel'] = Field(
        description=BaseModel.model_fields['model_name'].description
    )
    class_name: str = 'Action'

    adapter_class_name: str = Field(
        'BaseAdapter',
        description='Adapter Processor Name',
    )

    config: BaseActionConfigModel = Field(
        BaseActionConfigModel(),
        description='Configuration Passed to Adapter to execute the Action',

    )

    # when not set explicitly, same as id. Used to distinguish two or more same actions, but executed in the same test scenario
    execution_id: str = Field(
        '',
        description='Unique Execution Id per scenario',

    )

    @model_validator(mode="before")
    def check_execution_id(self):
        if not self.get('execution_id'):
            self['execution_id'] = self.get('id')

        reserved_execution_ids = [enum.value for enum in ReservedExecutionId]
        candidate_execution_id = self['execution_id']
        if candidate_execution_id in reserved_execution_ids:
            logger.error(f"Your Execution Id must not be one of {reserved_execution_ids}")
            raise ReservedKeywordsException(offending_keyword=candidate_execution_id,
                                            reserved_keywords=reserved_execution_ids)

        return self

    start_time: Union[int,float] = Field(
        -1,
        description='Start Time, number of seconds passed since epoch',
    )

    end_time: Union[int,float] = Field(
        -1,
        description='End Time, number of seconds passed since epoch',
    )

    @property
    def uid(self):
        """
        Action uses execution_id as unique_id.
        """
        return self.execution_id

    @property
    def elapsed_time(self) -> float:
        """
        Elapsed Seconds
        Returns
        -------

        """
        if self.start_time > 0 and self.end_time > 0:
            return self.end_time - self.start_time
        else:
            return -1

    pre_hook_context: Dict[str, str] = Field(
        {},
        description='Suitable for rendering **stateful** jinja globals \n'
                    'The returned value is stored in a variable, accessible by subsequent rendering by other config fields \n'
    )

    @field_validator('pre_hook_context', mode="before")
    @classmethod
    def check_pre_hook_context(cls, value):
        if not value:
            value = {}
        return value

    api_protocol: ActionAPIProtocolEnum = Field(
        ActionAPIProtocolEnum.UNDEFINED,
        description='API Protocol',
    )

    # To be set by Adapter, not by user
    state: ActionStateEnum = Field(
        ActionStateEnum.PENDING,
        description='Action State',
    )
    input: BaseActionInputModel = Field(
        BaseActionInputModel(),
        description='Action Input',
    )
    output: BaseActionOutputModel = Field(
        BaseActionOutputModel(),
        description='Action Output',
    )
    response_status: OtherResponseStatusEnum = Field(
        OtherResponseStatusEnum.UNITIALISED_STATUS,
        description='Actual Response Status',
    )

    exec: Optional[str] = Field(
        None,
        description='Exception Message when Action is in Error State'
    )

    _exec: Optional[Exception] = Field(
        None,
        description='Exception Instance thrown when Action is in Error State',
        exclude=True,
    )

    schemas: List[BaseSchemaModel] = Field(
        [],
        description='List of Schemas used to validate against the response'
    )

    schema_validators: List[BaseSchemaValidatorModel] = Field(
        [],
        description='List of Schema Validation Configurations',
    )

    @field_validator('schemas', 'schema_validators', mode="before")
    @classmethod
    def check_list(cls, value: Any):
        if not value:
            return []
        else:
            return value

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if isinstance(other, BaseActionModel):
            return self.execution_id == other.execution_id
        return False
