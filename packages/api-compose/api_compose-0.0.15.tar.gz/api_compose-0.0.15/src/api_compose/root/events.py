from api_compose.core.events.base import BaseEvent, BaseData, EventType


class SessionEvent(BaseEvent):
    event: EventType = EventType.Session
    data: BaseData = BaseData()


class SpecificationEvent(BaseEvent):
    event: EventType = EventType.Specification
    data: BaseData = BaseData()

class ScenarioEvent(BaseEvent):
    event: EventType = EventType.Scenario
    data: BaseData = BaseData()
