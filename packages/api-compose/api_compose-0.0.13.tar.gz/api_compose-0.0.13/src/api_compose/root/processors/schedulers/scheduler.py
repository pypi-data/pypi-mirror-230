import traceback

from api_compose.core.events.scheduler import SchedulerEvent
from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.core.logging import get_logger
from api_compose.core.utils.base_scheduler import BaseScheduler
from api_compose.root.models.scenario import ScenarioModel
from api_compose.root.processors.schedulers.utils import convert_edges_from_str_to_model
from api_compose.services.composition_service.events.executor import ExecutorEvent
from api_compose.services.composition_service.jinja.context import ActionJinjaContext
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel
from api_compose.services.composition_service.models.actions.states import ActionStateEnum
from api_compose.services.composition_service.processors.actions import Action
from api_compose.services.composition_service.processors.executors.base_executor import BaseExecutor
from api_compose.services.persistence_service.processors.base_backend import BaseBackend

logger = get_logger(__name__)



class ActionScheduler(BaseScheduler):

    def __init__(self,
                 executor: BaseExecutor,
                 backend: BaseBackend,
                 jinja_engine: JinjaEngine,
                 scenario_model: ScenarioModel,
                 *args,
                 **kwargs,
                 ):
        super().__int__(
            *args,
            nodes=scenario_model.actions,
            edges=convert_edges_from_str_to_model(
                is_schedule_linear=scenario_model.config.scheduler_config.is_schedule_linear,
                custom_schedule_order=scenario_model.config.scheduler_config.custom_schedule_order,
                action_models=scenario_model.actions,
            ),
            max_concurrent_node_execution_num=scenario_model.config.scheduler_config.max_concurrent_node_execution_num,
            rescan_all_nodes_in_seconds=scenario_model.config.scheduler_config.rescan_all_nodes_in_seconds,
            **kwargs
        )
        self.backend = backend
        self.jinja_engine = jinja_engine
        self.executor = executor
        self.scenario_model = scenario_model

    def is_node_successful(self, node: BaseActionModel) -> bool:
        logger.debug(f"Polling node {node.fqn=} - {node.state=}", SchedulerEvent())
        return node.state == ActionStateEnum.ENDED

    def is_node_done(self, node: BaseActionModel) -> bool:
        logger.debug(f"Polling node {node.fqn=} - {node.state=}", SchedulerEvent())
        return node.state in [ActionStateEnum.ERROR, ActionStateEnum.ENDED, ActionStateEnum.DISCARDED]

    def execute_node(self, node: BaseActionModel, skip: bool) -> None:
        logger.info(f'{node.fqn}: Executing action model {node.uid=} - {skip=}', SchedulerEvent())
        if skip:
            node.state = ActionStateEnum.DISCARDED
        else:
            try:
                jinja_context: ActionJinjaContext = ActionJinjaContext.build(
                    backend=self.backend,
                    action_model=node
                )
                action = Action(action_model=node, backend=self.backend, jinja_engine=self.jinja_engine)
                self.executor.execute(action, jinja_context)
            except Exception as e:
                # Assign Error Status to Action when there's any exception
                logger.error(traceback.format_exc(), ExecutorEvent())
                node._exec = e
                node.exec = traceback.format_exc()
                node.state = ActionStateEnum.ERROR
                raise
