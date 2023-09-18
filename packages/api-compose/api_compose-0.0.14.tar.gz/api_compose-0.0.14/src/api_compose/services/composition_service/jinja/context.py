from __future__ import annotations

from typing import List

from pydantic import Field

from api_compose.services.persistence_service.processors.base_backend import BaseBackend
from api_compose.core.jinja.core.context import BaseJinjaContext
from api_compose.services.common.models.base import BaseModel
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel


class ActionJinjaContext(BaseJinjaContext, extra='allow'):
    """
    Scenario-Scoped Context

    Used to render templated fields in actions. e.g. {{ acp.actions.output_body() }}
    """

    action_models: List[BaseActionModel] = Field([], description='List of Action Models not in pending states')
    current_action_model: BaseActionModel = Field(description='Current action model')

    # Other pre-hook

    @classmethod
    def build(cls,
              backend: BaseBackend,
              action_model: BaseActionModel,
              append_current_action_model=True,
              ) -> ActionJinjaContext:
        # Set current action model
        c = ActionJinjaContext(current_action_model=action_model)

        # Set actions models
        base_models: List[BaseModel] = backend.get_latest_siblings(action_model)
        c.action_models = [model for model in base_models if isinstance(model, BaseActionModel)]

        if append_current_action_model:
            c.action_models.append(action_model)

        return c
