from __future__ import annotations

__all__ = ["BaseAdapter"]

import time
import traceback
from abc import ABC, abstractmethod

from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.core.logging import get_logger
from api_compose.core.utils.exceptions import ReservedKeywordsException
from api_compose.services.common.processors.base import BaseProcessor
from api_compose.services.composition_service.events.action import ActionData, ActionEvent
from api_compose.services.composition_service.jinja.context import ActionJinjaContext
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel
from api_compose.services.composition_service.models.actions.inputs.base_inputs import BaseActionInputModel
from api_compose.services.composition_service.models.actions.outputs.base_outputs import BaseActionOutputModel
from api_compose.services.composition_service.models.actions.states import ActionStateEnum
from api_compose.services.composition_service.models.protocols.hints import ResponseStatusEnum
from api_compose.services.composition_service.models.protocols.status_enums import OtherResponseStatusEnum

logger = get_logger(name=__name__)


class BaseAdapter(BaseProcessor, ABC):
    """
    Network Communication
    """

    OUTPUT_BODY_KEY = 'message'
    ERROR_OUTPUT_BODY: str = ""

    def __init__(
            self,
            action_model: BaseActionModel,
            jinja_engine: JinjaEngine,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.action_model = action_model
        self.jinja_engine: JinjaEngine = jinja_engine
        self.input: BaseActionInputModel = BaseActionInputModel()
        self.output: BaseActionOutputModel = BaseActionOutputModel()
        self.response_status: ResponseStatusEnum = (
            OtherResponseStatusEnum.UNITIALISED_STATUS
        )

        # Initialise state
        state = ActionStateEnum.PENDING
        logger.info(f"Action %s is in state %s" % (self.action_model.fqn, state),
                    ActionEvent(data=ActionData(id=self.action_model.fqn, state=state)))
        self.action_model.state = state

    def _merge_pre_hook_context(self, jinja_context: ActionJinjaContext) -> ActionJinjaContext:
        additional_context = {}
        reserved_keywords = [key for key in ActionJinjaContext.model_fields]

        for var, template in self.action_model.pre_hook_context.items():
            if var in reserved_keywords:
                raise ReservedKeywordsException(offending_keyword=var, reserved_keywords=reserved_keywords)

            str_, is_success, exec = self.jinja_engine.set_template_by_string(template).render_to_str()

            if not is_success:
                raise exec
            else:
                additional_context[var] = str_

        # Use dict(jinja_context) to keep the original objects. No more validation is required for original jinja_context
        return ActionJinjaContext(**dict(jinja_context), **additional_context)

    @abstractmethod
    def _on_start(self, jinja_context: ActionJinjaContext):
        """
        Hook before calling self.on_exchange().
        :return:
        """
        self.jinja_context: ActionJinjaContext = self._merge_pre_hook_context(jinja_context)

        state = ActionStateEnum.STARTED
        self.action_model.start_time = time.time()

        logger.info(f"Action %s is in state %s" % (self.action_model.fqn, state),
                    ActionEvent(data=ActionData(id=self.action_model.fqn, state=state)))
        self.action_model.state = state

    @abstractmethod
    def _on_exchange(self):
        """
        Main method to connect with different systems.

        :return:
        """
        state = ActionStateEnum.RUNNING
        logger.info(f"Action %s is in state %s" % (self.action_model.fqn, state),
                    ActionEvent(data=ActionData(id=self.action_model.fqn, state=state)))
        self.action_model.state = state

    @abstractmethod
    def _set_response_status(self):
        """
        Set self.status

        Return the status after calling self.connect()
        :return:
        """
        pass

    @abstractmethod
    def _set_input(self):
        """
        Set self.input.

        Return a dictionary of rendered input used in calling self.connect()
        :return:
        """
        pass

    @abstractmethod
    def _set_output(self):
        """
        Set self.output

        Return a dictionary of output from calling self.on_exchange()
        :return:
        """
        pass

    @abstractmethod
    def _on_error(self, exception: Exception):
        """
        Hook to handle error.
        :return:
        """
        state = ActionStateEnum.ERROR
        logger.error(f"Action %s is in state %s" % (self.action_model.fqn, state),
                     ActionEvent(data=ActionData(id=self.action_model.fqn, state=state)))
        self.action_model.state = state
        self.action_model.exec = traceback.format_exc()
        self.action_model._exec = exception

    @abstractmethod
    def _on_end(self):
        """
        Hook to postprocess stuff
        :return:
        """
        state = ActionStateEnum.ENDED
        self.action_model.end_time = time.time()

        logger.info(f"Action %s is in state %s" % (self.action_model.fqn, state),
                    ActionEvent(data=ActionData(id=self.action_model.fqn, state=state)))
        self.action_model.state = state

    @abstractmethod
    def start(self, jinja_context: ActionJinjaContext):
        try:
            # Might error on_start when rendering
            self._on_start(jinja_context=jinja_context)
            # Might error on_exchange when doing network call
            self._on_exchange()
        except Exception as e:
            self._on_error(e)
            logger.error(traceback.format_exc(),
                         ActionEvent(data=ActionData(id=self.action_model.fqn, state=ActionStateEnum.ERROR)))
        else:
            self._on_end()
            self._set_input()
            self.action_model.input = self.input
            self._set_output()
            self.action_model.output = self.output
            self._set_response_status()
            self.action_model.response_status = self.response_status

    @abstractmethod
    def stop(self):
        logger.debug("stop() in not implemented", ActionEvent(data=ActionData(id=self.action_model.fqn)))
