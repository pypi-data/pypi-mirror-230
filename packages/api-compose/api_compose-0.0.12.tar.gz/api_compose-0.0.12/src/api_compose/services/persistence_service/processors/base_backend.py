__all__ = ['BaseBackend']

from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar

from api_compose.services.common.models.base import BaseModel
from api_compose.services.common.processors.base import BaseProcessor

BaseModelSubClass = TypeVar('BaseModelSubClass', bound=BaseModel)

class BaseBackend(BaseProcessor, ABC):
    """
    Base Class which defines the storage implementation
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def get_latest_by_fqn(
        self, fqn: str
    ) -> Optional[BaseModelSubClass]:
        pass

    @abstractmethod
    def get_latest_siblings(self, base_model: BaseModel) -> List[BaseModelSubClass]:
        pass

    @abstractmethod
    def add(self, model: BaseModel):
        assert isinstance(model, BaseModel), f'Only BaseComponentModel and its subclasses are allowed. Yours is {type(model)}'
        pass

