from typing import Union

from api_compose.services.composition_service.models.protocols.status_enums import HttpResponseStatusEnum, \
    WebSocketResponseStatusEnum, OtherResponseStatusEnum

ResponseStatusEnum = Union[HttpResponseStatusEnum, WebSocketResponseStatusEnum, OtherResponseStatusEnum]
