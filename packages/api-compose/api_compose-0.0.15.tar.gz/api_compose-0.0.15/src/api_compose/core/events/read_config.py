from typing import Dict, Optional

from api_compose.core.events.base import BaseEvent, BaseData, EventType


# Read Config
class ReadConfigData(BaseData):
    kv: Dict = {}

class ReadConfigEvent(BaseEvent):
    event: EventType = EventType.ReadConfiguration
    data: ReadConfigData



