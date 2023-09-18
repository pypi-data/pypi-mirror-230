from api_compose.core.events.base import BaseData, BaseEvent, EventType


class TextFieldEvent(BaseEvent):
    event: EventType = EventType.TextField
    data: BaseData = BaseData()
