from typing import Literal

from pydantic import Field

from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel
from api_compose.services.composition_service.models.actions.configs.dummy_configs import DummyActionConfigModel
from api_compose.services.composition_service.models.actions.inputs.dummy_inputs import DummyActionInputModel
from api_compose.services.composition_service.models.actions.outputs.dummy_outputs import DummyActionOutputModel


class DummyActionModel(BaseActionModel):
    """
    Dummy Action.

    """
    model_name: Literal['DummyActionModel'] = Field(
        'DummyActionModel',
        description=BaseActionModel.model_fields['model_name'].description
    )



    adapter_class_name: str = Field(
        'DummyAdapter',
        description=BaseActionModel.model_fields['adapter_class_name'].description,
    )

    config: DummyActionConfigModel = Field(
        DummyActionConfigModel(),
        description=BaseActionModel.model_fields['config'].description,
    )

    input: DummyActionInputModel = Field(
        DummyActionInputModel(),
        description=BaseActionModel.model_fields['input'].description,
    )
    output: DummyActionOutputModel = Field(
        DummyActionOutputModel(),
        description=BaseActionModel.model_fields['output'].description,
    )
