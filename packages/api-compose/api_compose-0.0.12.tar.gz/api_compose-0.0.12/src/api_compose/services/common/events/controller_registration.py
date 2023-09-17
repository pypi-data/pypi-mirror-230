from typing import Type

from api_compose.core.events.base import BaseEvent, EventType, BaseData
from api_compose.services.common.processors.base import BaseProcessor


class ProcessorRegistrationData(BaseData):
    processor_class: Type[BaseProcessor]


# Registration
class ProcessorRegistrationEvent(BaseEvent):
    event: EventType = EventType.ProcessorRegistration
    data: ProcessorRegistrationData
