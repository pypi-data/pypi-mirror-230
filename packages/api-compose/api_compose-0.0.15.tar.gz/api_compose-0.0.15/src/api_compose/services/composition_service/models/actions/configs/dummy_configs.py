from __future__ import annotations

from pydantic import Field

from api_compose.services.common.models.text_field.templated_text_field import IntegerTemplatedTextField
from api_compose.services.composition_service.models.actions.configs.base_configs import BaseActionConfigModel


class DummyActionConfigModel(BaseActionConfigModel):
    sleep_seconds: IntegerTemplatedTextField = Field(
        IntegerTemplatedTextField(template='0'),
        description='Templateable Sleep Seconds',
    )
