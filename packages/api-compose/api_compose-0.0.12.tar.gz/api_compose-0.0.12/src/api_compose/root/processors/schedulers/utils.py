from typing import List, Tuple

from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel


def get_action_model_by_execution_id(execution_id: str, action_models: List[BaseActionModel]):
    for action_model in action_models:
        if action_model.execution_id == execution_id:
            return action_model


def convert_edges_from_str_to_model(
        is_schedule_linear: bool,
        custom_schedule_order: List[Tuple[str, str]],
        action_models: List[BaseActionModel],
) -> List[Tuple[BaseActionModel, BaseActionModel]]:
    edges: List[Tuple[BaseActionModel, BaseActionModel]] = []

    if is_schedule_linear:
        if len(action_models) == 0:
            pass
        else:
            for i in range(len(action_models) - 1):
                edges.append((action_models[i], action_models[i + 1]))
    else:
        for edge_str in custom_schedule_order:
            edges.append((get_action_model_by_execution_id(edge_str[0], action_models),
                          get_action_model_by_execution_id(edge_str[1], action_models)))

    return edges
