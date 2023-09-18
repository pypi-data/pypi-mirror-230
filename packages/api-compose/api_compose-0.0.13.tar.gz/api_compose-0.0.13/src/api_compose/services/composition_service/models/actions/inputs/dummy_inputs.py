from pydantic import Field

from api_compose.services.composition_service.models.actions.inputs.base_inputs import BaseActionInputModel


class DummyActionInputModel(BaseActionInputModel):
    sleep_seconds: int = Field(
        -1,
        description='Number of seconds to sleep'
    )
