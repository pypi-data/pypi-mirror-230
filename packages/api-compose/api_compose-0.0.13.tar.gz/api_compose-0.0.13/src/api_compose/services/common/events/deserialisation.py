from api_compose.core.events.base import BaseEvent, EventType, BaseData


class DeserialisationEvent(BaseEvent):
    event: EventType = EventType.Deserialisation
    data: BaseData = BaseData()
