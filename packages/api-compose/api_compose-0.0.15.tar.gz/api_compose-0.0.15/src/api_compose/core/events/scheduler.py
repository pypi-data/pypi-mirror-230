from api_compose.core.events.base import EventType, BaseEvent, BaseData


class SchedulerEvent(BaseEvent):
    event: EventType = EventType.Scheduler
    data: BaseData = BaseData()
