import json
from typing import List


class ExecutionIdNonUniqueException(Exception):
    def __init__(self,
                 scenario_id: str,
                 execution_ids: List[str]
                 ):
        self.scenario_id = scenario_id
        self.execution_ids = execution_ids

    def __str__(self):
        return f"""Scenario {self.scenario_id} has non-unique execution ids {json.dumps(self.execution_ids, indent=4)} """
