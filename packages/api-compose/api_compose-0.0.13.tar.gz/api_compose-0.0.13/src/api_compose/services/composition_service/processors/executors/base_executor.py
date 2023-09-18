__all__ = ["BaseExecutor"]

from abc import ABC, abstractmethod

from api_compose.services.common.processors.base import BaseProcessor
from api_compose.services.composition_service.jinja.context import ActionJinjaContext
from api_compose.services.composition_service.processors.actions import Action


class BaseExecutor(BaseProcessor, ABC):
    """
    Base class which defines the platform on which an action is executed.
    """

    def __init__(self,
                 *args,
                 **kwargs,
                 ):
        super().__init__()

    @abstractmethod
    def execute(self, action: Action, jinja_context: ActionJinjaContext):
        """
        Implementation of how each action is executed
        Parameters
        ----------
        action
        jinja_context

        Returns
        -------

        """
        pass
