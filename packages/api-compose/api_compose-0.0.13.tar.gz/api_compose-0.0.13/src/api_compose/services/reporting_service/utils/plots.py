import datetime

from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import networkx as nx

from api_compose.core.logging import get_logger
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel

logger = get_logger(__name__)


def dump_actions_digraph(digraph: nx.DiGraph, dump_file_path: Path):
    logger.info(f'Dumping Graph to path {dump_file_path=}')
    # Get mapping
    labels = {}
    for node, data in nx.get_node_attributes(digraph, 'data').items():
        data: BaseActionModel = data
        labels[node] = dict(data).get('execution_id')

    # Clear canvas
    plt.clf()
    nx.draw(digraph, pos=nx.spring_layout(digraph), labels=labels, with_labels=True)
    plt.draw()
    plt.savefig(dump_file_path)


def dump_actions_duration_graph(actions: List[BaseActionModel], dump_file_path: Path):
    # Clear canvas
    plt.clf()

    scenario_id = actions[0].parent_ids[-1]

    # Sorting and filter the actions based on their start_time
    actions.sort(key=lambda x: x.start_time)
    actions = [action for action in actions if action.start_time > 0 and action.end_time > 0]

    if len(actions) == 0:
        logger.warning('No actions are run. Not generating any duration graph.....')
        return




    # Normalizing the start and end times
    min_time = min(actions, key=lambda x: x.start_time).start_time
    normalized_start_times = [action.start_time - min_time for action in actions]
    normalized_end_times = [action.end_time - min_time for action in actions]
    execution_ids = [action.execution_id for action in actions]

    # Setting up the plot
    fig, ax = plt.subplots()

    # Setting the y-axis ticks and labels
    y_ticks = range(len(actions))
    y_tick_labels = execution_ids
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_tick_labels)

    # Plotting the horizontal bars as durations
    ax.barh(y_ticks, normalized_end_times, left=normalized_start_times, height=0.5, align='center', alpha=0.8)

    # Formatting the x-axis as durations
    ax.set_xlabel('Duration')
    ax.set_xlim(0, max(normalized_end_times))

    # Customizing the x-axis ticks and labels
    x_ticks = ax.get_xticks()
    x_tick_labels = ['{:.2f}'.format(x) for x in x_ticks]
    ax.xaxis.set_major_locator(plt.FixedLocator(x_ticks))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(x_tick_labels))
    # Rotating the x-axis tick labels diagonally
    plt.xticks(rotation=30, ha='right')

    # Setting the plot title
    ax.set_title(f'Action Timeline for {scenario_id}')

    # Displaying the plot
    plt.draw()
    plt.savefig(dump_file_path)
