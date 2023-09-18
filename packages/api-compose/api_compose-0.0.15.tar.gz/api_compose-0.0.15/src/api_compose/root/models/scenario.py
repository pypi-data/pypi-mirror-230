import os
from enum import Enum
from typing import List, Any, Union, Literal, Annotated

from pydantic import BaseModel as _BaseModel, ConfigDict, field_validator, model_validator
from pydantic import Field

from api_compose.core.logging import get_logger
from api_compose.core.utils.list import get_duplicates_in_list
from api_compose.root.exceptions import ExecutionIdNonUniqueException
from api_compose.root.models.schedulers.configs import ActionSchedulerConfigModel
from api_compose.services.assertion_service.models.jinja_assertion import JinjaAssertionModel
from api_compose.services.common.models.base import BaseModel
from api_compose.services.common.models.functional_testing import FunctionalTestingEnum
from api_compose.services.common.models.ref_resolver import RefResolverModel
from api_compose.services.common.processors.ref_resolver import RefResolver
from api_compose.services.common.registry.processor_registry import ProcessorRegistry
from api_compose.services.composition_service.models.actions.actions.dummy_action import DummyActionModel
from api_compose.services.composition_service.models.actions.actions.http_actions import JsonHttpActionModel, \
    XmlHttpActionModel
from api_compose.services.composition_service.models.actions.actions.websocket_actions import \
    JsonRpcWebSocketActionModel
from api_compose.services.composition_service.models.actions.states import ActionStateEnum
from api_compose.services.composition_service.models.executors.configs import BaseExecutorConfigModel, \
    LocalExecutorConfigModel
from api_compose.services.composition_service.models.executors.enum import ExecutorProcessorEnum

logger = get_logger(__name__)


class ExecutionIdAssignmentEnum(Enum):
    Positional = 'Positional'
    UserDefined = 'UserDefined'


class ScenarioModelConfig(_BaseModel):
    executor: ExecutorProcessorEnum = Field(
        ExecutorProcessorEnum.LocalExecutor,
        description='Executor Implementation to use',
    )
    executor_config: BaseExecutorConfigModel = Field(
        LocalExecutorConfigModel(),
        description='Config required by Executor Implementation',
    )

    scheduler_config: ActionSchedulerConfigModel = Field(
        ActionSchedulerConfigModel(),
        description='Config required by the Action Scheduler',
    )


class ScenarioModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_name: Literal['ScenarioModel'] = Field(
        description=BaseModel.model_fields['model_name'].description
    )

    config: ScenarioModelConfig = ScenarioModelConfig()
    functional_testing: FunctionalTestingEnum = FunctionalTestingEnum.HappyPath
    execution_id_assignment: ExecutionIdAssignmentEnum = Field(
        ExecutionIdAssignmentEnum.UserDefined,
        description='When Positional, each Action in then scenario will be assigned a numeric execution_id starting from one.'
                    'When User Defined, each Action will retain the execution_id assigned by the user.',
    )
    actions: List[
        Annotated[Union[
            JsonRpcWebSocketActionModel, XmlHttpActionModel, JsonHttpActionModel, DummyActionModel],
        Field(discriminator='model_name')
        ]
    ]

    assertions: List[JinjaAssertionModel] = []

    @field_validator("actions", mode="before")
    @classmethod
    def parse_actions(cls, value: Any):
        """
        Resolve RefResolverModel
        """
        list_ = []
        assert type(value) == list, "Please supply a list of actions"
        for action in value:
            if isinstance(action, _BaseModel):
                action = dict(action)

            model = ProcessorRegistry.create_model_by_model_name(
                action.get('model_name'),
                action,
            )
            if isinstance(model, RefResolverModel):
                model = RefResolver(
                    model,
                ).resolve()
            list_.append(model)

        return list_

    @model_validator(mode="after")
    def assign_execution_id(self):
        """
        Create Actions and Assertions with the appropriate Model Type
        """
        if self.execution_id_assignment == ExecutionIdAssignmentEnum.Positional:
            cnt = 0
            for action in self.actions:
                cnt += 1
                action.execution_id = str(cnt)
        return self  # return so that it has no error

    @model_validator(mode="after")
    def validate_execution_id(self):
        """
        Validate no two actions in same scenario have same execution_id
        """
        fqns = [action.fqn for action in self.actions]
        duplicate_keys = get_duplicates_in_list([key for key in fqns])
        if len(duplicate_keys) != 0:
            logger.error(
                f"Error: Actions in Scenario {self.fqn} with the same execution id found! {os.linesep} {os.linesep.join([fqn for fqn in fqns])}")
            raise ExecutionIdNonUniqueException(
                scenario_id=self.fqn,
                execution_ids=fqns
            )

        return self  # return so that it has no error

    @property
    def actions_duration_file_name(self) -> str:
        return self.fqn.replace('.', '-') + '.png'

    start_time: Union[int, float] = Field(
        -1,
        description='Start Time, number of seconds passed since epoch',

    )
    end_time: Union[int, float] = Field(
        -1,
        description='End Time, number of seconds passed since epoch',

    )

    @property
    def is_success(self):
        return (all(assertion_item.is_success for assertion_item in self.assertions)
                and all(action.state == ActionStateEnum.ENDED for action in self.actions))

    @property
    def elapsed_time(self) -> float:
        if self.start_time > 0 and self.end_time > 0:
            return self.end_time - self.start_time
        else:
            return -1
