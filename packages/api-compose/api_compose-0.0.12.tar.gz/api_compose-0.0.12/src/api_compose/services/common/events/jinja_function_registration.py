from api_compose.core.events.base import BaseData, BaseEvent, EventType


class JinjaFunctionRegistrationEvent(BaseEvent):
    event: EventType = EventType.JinjaFunctionRegistration
    # state:
    data: BaseData() = BaseData()
