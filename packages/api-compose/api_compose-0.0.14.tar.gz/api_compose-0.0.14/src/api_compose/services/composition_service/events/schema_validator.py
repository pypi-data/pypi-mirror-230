from api_compose.core.events.base import BaseEvent, BaseData, EventType


class SchemaValidatorEvent(BaseEvent):
    event: EventType = EventType.SchemaValidator
    # state:
    data: BaseData = BaseData()
