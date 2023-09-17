import uuid
from typing import List, Literal

from pydantic import Field

from api_compose.root.models.specification import SpecificationModel
from api_compose.services.common.models.base import BaseModel


class SessionModel(BaseModel):
    id: str
    description: str = ''

    specifications: List[SpecificationModel]

    @property
    def is_success(self) -> bool:
        return all([spec.is_success for spec in self.specifications])
