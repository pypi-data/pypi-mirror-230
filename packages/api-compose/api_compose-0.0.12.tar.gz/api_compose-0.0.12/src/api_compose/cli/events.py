from api_compose.core.events.base import BaseEvent, BaseData, EventType




class DiscoveryEvent(BaseEvent):
    event: EventType = EventType.Discovery
    data: BaseData = BaseData()
