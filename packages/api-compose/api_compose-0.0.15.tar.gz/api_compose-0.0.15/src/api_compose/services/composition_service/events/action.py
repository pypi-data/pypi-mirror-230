from api_compose.core.events.base import BaseEvent, BaseData, EventType
from api_compose.services.composition_service.models.actions.states import ActionStateEnum


class ActionData(BaseData):
    id: str
    state: ActionStateEnum = ActionStateEnum.PENDING


class ActionEvent(BaseEvent):
    event: EventType = EventType.Action
    # state:
    data: ActionData
