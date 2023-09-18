from typing import Tuple, List, Union

from pydantic import BaseModel as _BaseModel, Field


class ActionSchedulerConfigModel(_BaseModel):
    max_concurrent_node_execution_num: int = 5
    rescan_all_nodes_in_seconds: Union[int, float] = 0.5

    is_schedule_linear: bool = Field(
        True,
        description='When true, actions will be scheduled linearly in the order they are provided in the manifest. custom_schedule_order will be ignored.'
                    'When false, custom_schedule_order will be used as schedule order'
    )
    custom_schedule_order: List[Tuple[str, str]] = Field(
        [],
        description='When is_schedule_linear is True, this field is ignored'
                    'When is_schedule_linear is False, an empty custom_schedule_order means all actions will be executed in parallel'
    )
