from api_compose.core.events.base import BaseEvent, BaseData, EventType


class ExecutorEvent(BaseEvent):
    event: EventType = EventType.Executor
    # state:
    data: BaseData = BaseData()
