from api_compose.core.events.base import BaseEvent, BaseData, EventType


class AssertionEvent(BaseEvent):
    event: EventType = EventType.Assertion
    data: BaseData = BaseData()


