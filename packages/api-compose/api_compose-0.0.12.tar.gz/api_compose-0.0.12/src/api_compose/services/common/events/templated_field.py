from api_compose.core.events.base import BaseData, BaseEvent, EventType


class TemplatedFieldEvent(BaseEvent):
    event: EventType = EventType.TemplatedField
    data: BaseData = BaseData()
