from api_compose.core.events.base import EventType, BaseEvent, BaseData


class JinjaRenderingEvent(BaseEvent):
    event: EventType = EventType.JinjaRendering
    data: BaseData = BaseData()
