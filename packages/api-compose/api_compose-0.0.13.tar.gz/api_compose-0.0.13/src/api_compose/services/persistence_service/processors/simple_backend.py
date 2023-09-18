__all__ = ["SimpleBackend", ]

from typing import List, Optional

from api_compose.core.logging import get_logger
from api_compose.services.common.models.base import BaseModel
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.persistence_service.processors.base_backend import BaseBackend, \
    BaseModelSubClass

logger = get_logger(name=__name__)


def get_descendant_classes(cls):
    descendants = cls.__subclasses__()
    for descendant in descendants:
        descendants += get_descendant_classes(descendant)
    return descendants


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.Backend,
    models=[
        # No models required
    ]
)
class SimpleBackend(BaseBackend):
    """
    A simple backend which stores data in-memory.

    Throw error when the key  was already occupied

    Uses the BaseComponentModel's fqn as unique key
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry: List[BaseModel] = []

    def add(self, model: BaseModel):
        super().add(model)
        # Get rid of existing component
        self.registry = [elem for elem in self.registry if elem != model]
        self.registry.append(model)

    def get_latest_by_fqn(self, fqn: str) -> Optional[BaseModelSubClass]:
        for model in self.registry:
            if model.fqn == fqn:
                return model

    def get_latest_siblings(self, base_model: BaseModel) -> List[BaseModelSubClass]:
        return [elem for elem in self.registry if elem.ancestry == base_model.ancestry]
