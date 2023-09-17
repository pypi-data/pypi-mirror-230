from typing import List, Dict, Any

from api_compose.core.logging import get_logger
from api_compose.core.utils.exceptions import CircularDependencyException, NonExistentNodeException

logger = get_logger(__name__)


def get_unique_list(list_: List[Any]) -> List[Any]:
    return [item for i, item in enumerate(list_) if item not in list_[:i]]





def get_linear_execution_order(nodes_with_dependencies: Dict[str, List[str]]) -> List[str]:
    # Create a dictionary to store the nodes and their dependencies
    node_dependencies = {}
    for node, dependencies in nodes_with_dependencies.items():
        node_dependencies[node] = get_unique_list(dependencies)

    # Create a set to store the nodes that have been visited
    visited_nodes = set()

    # Create a set to store the nodes that are currently being visited
    visiting_nodes = set()

    # Create a list to store the order in which the nodes should be executed
    execution_order = []

    # Define a helper function to visit the nodes recursively
    def visit(node):
        if node in visiting_nodes:
            raise CircularDependencyException(visiting_nodes=visiting_nodes, offending_node=node)
        if node in visited_nodes:
            return
        visiting_nodes.add(node)
        deps = node_dependencies.get(node)
        if deps is None:
            raise NonExistentNodeException(non_existent_node=node, nodes=[node for node in nodes_with_dependencies.keys()])
        else:
            for dep in deps:
                visit(dep)
        visiting_nodes.remove(node)
        visited_nodes.add(node)
        execution_order.append(node)

    # Visit each node in the graph
    for node in node_dependencies:
        visit(node)

    return execution_order

