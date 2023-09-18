import time

from api_compose.core.logging import get_logger
from api_compose.services.common.models.text_field.templated_text_field import IntegerTemplatedTextField
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.composition_service.events.action import ActionEvent, ActionData
from api_compose.services.composition_service.jinja.context import ActionJinjaContext
from api_compose.services.composition_service.models.actions.actions.dummy_action import DummyActionModel
from api_compose.services.composition_service.models.actions.inputs.dummy_inputs import DummyActionInputModel
from api_compose.services.composition_service.models.actions.outputs.dummy_outputs import DummyActionOutputModel
from api_compose.services.composition_service.models.actions.states import ActionStateEnum
from api_compose.services.composition_service.models.protocols.status_enums import OtherResponseStatusEnum
from api_compose.services.composition_service.processors.adapters.base_adapter import BaseAdapter

logger = get_logger(__name__)


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.Adapter,
    models=[  # Define Action instead
    ]
)
class DummyAdapter(BaseAdapter):
    """
    Dummy Adapter which does Nothing

    """

    def __init__(
            self,
            action_model: DummyActionModel,
            *args,
            **kwargs,
    ):
        super().__init__(action_model, *args, **kwargs)
        self.sleep_seconds: IntegerTemplatedTextField = action_model.config.sleep_seconds
        pass

    def _on_start(self, jinja_context: ActionJinjaContext):
        super()._on_start(jinja_context)
        self.sleep_seconds_obj = self.sleep_seconds.render_to_text(jinja_engine=self.jinja_engine,
                                                                   jinja_context=self.jinja_context).deserialise_to_obj().obj

    def _on_exchange(self):
        super()._on_exchange()
        logger.info(
            f'Action %s sleeping for %s seconds' % (self.action_model.fqn, self.sleep_seconds_obj),
            ActionEvent(
                data=ActionData(
                    id=self.action_model.fqn, state=ActionStateEnum.RUNNING,
                    input={'sleep_seconds': self.sleep_seconds_obj, }
                )
            )
        )
        time.sleep(self.sleep_seconds_obj)

    def _on_error(self, exception: Exception):
        super()._on_error(exception)

    def _on_end(self):
        super()._on_end()

    def _set_response_status(self):
        self.response_status = OtherResponseStatusEnum.EXECUTED

    def _set_input(self):
        self.input = DummyActionInputModel(
            sleep_seconds=self.sleep_seconds_obj,
        )

    def _set_output(self):
        self.output = DummyActionOutputModel(
            status_code=OtherResponseStatusEnum.EXECUTED.value
        )

    def start(self, jinja_context: ActionJinjaContext):
        super().start(jinja_context)

    def stop(self):
        super().stop()
