from typing import List

from api_compose.root.models.scenario import ScenarioModel
from api_compose.services.common.models.base import BaseModel


class SpecificationModel(BaseModel):
    scenarios: List[ScenarioModel]


    @property
    def is_success(self) -> bool:
        return all([scenario.is_success for scenario in self.scenarios])

    @property
    def elapsed_time(self) -> float:
        return sum(scenario.elapsed_time for scenario in self.scenarios)

