from api_compose.core.events.base import BaseEvent, BaseData, EventType


class DefaultEvent(BaseEvent):
    event: EventType = EventType.Default
    data: BaseData = BaseData()
