__all__ = ["JsonRpcWebSocketAdapter"]

from typing import Union, Dict, List

from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.composition_service.processors.adapters.base_adapter import BaseAdapter


@ProcessorRegistry.set(
    processor_category=ProcessorCategory.Adapter,
    models=[
        # Add Action instead
    ]
)
class JsonRpcWebSocketAdapter(BaseAdapter):
    """
    JSON RPC Communication over WebSocket
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _set_output(self) -> Union[Dict, List]:
        pass
