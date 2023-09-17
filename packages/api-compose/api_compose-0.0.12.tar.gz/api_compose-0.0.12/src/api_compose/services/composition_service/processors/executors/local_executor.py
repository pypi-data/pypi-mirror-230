__all__ = ["LocalExecutor"]

from api_compose.core.logging import get_logger
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.composition_service.jinja.context import ActionJinjaContext
from api_compose.services.composition_service.processors.actions import Action
from api_compose.services.composition_service.processors.executors.base_executor import BaseExecutor

logger = get_logger(__name__)


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.Executor,
    models=[
        # Not required
    ]
)
class LocalExecutor(BaseExecutor):
    """
    Execute Each action on the same machine

    """

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

    def execute(self, action: Action, jinja_context: ActionJinjaContext):
        action.start(jinja_context)
        action.stop()
        action.validate_schema()


