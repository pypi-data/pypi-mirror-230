import concurrent
import time
from abc import ABC, abstractmethod
from concurrent.futures import Executor
from typing import List, Set, Tuple, Dict

import networkx as nx
from pydantic import BaseModel as _BaseModel

from api_compose.core.events.scheduler import SchedulerEvent
from api_compose.core.logging import get_logger

logger = get_logger(__name__)


class BaseScheduler(ABC):
    """
    Base Scheduler which determines which node in a graph of nodes is ready for execution.
    """

    def __int__(self,
                # Scheduler
                max_concurrent_node_execution_num: int,
                rescan_all_nodes_in_seconds: int,
                max_rescan_without_submit_cnt: int = 3,
                # Graph
                nodes: List[_BaseModel] = None,
                edges: List[Tuple[_BaseModel, _BaseModel]] = None,
                ):
        self.max_concurrent_node_execution_num = max_concurrent_node_execution_num
        self.rescan_all_nodes_in_seconds = rescan_all_nodes_in_seconds
        self.max_rescan_without_submit_cnt = max_rescan_without_submit_cnt
        self.nodes = nodes or []
        self.edges = edges or []

        self.digraph: nx.DiGraph = self._build_digraph()

    def _build_digraph(self) -> nx.DiGraph:
        # assert nodes in edge exist in self.nodes
        for edge in self.edges:
            assert edge[0] in self.nodes
            assert edge[1] in self.nodes

        dg = nx.DiGraph()

        for node in self.nodes:
            dg.add_node(id(node), data=node)

        for edge in self.edges:
            dg.add_edge(*(id(edge[0]), id(edge[1])))

        return dg

    @property
    def nodes_mapping(self) -> Dict[str, _BaseModel]:
        return nx.get_node_attributes(self.digraph, 'data')

    def run(self):
        total_rescan_cnt = 0
        rescan_with_submit_count = 0

        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_node_execution_num) as executor:
                total_rescan_cnt += 1
                logger.info("cnt=%s : traversing all nodes" % (total_rescan_cnt), SchedulerEvent())
                has_submit = False

                # Schedule work
                for node_id in self.digraph.nodes:
                    logger.info("cnt=%s : checking node_id=%s " % (total_rescan_cnt, node_id), SchedulerEvent())
                    node_id: str = node_id
                    node: _BaseModel = self.nodes_mapping.get(node_id)

                    if (not self.is_node_done(node)) and self.are_node_upstreams_done(node):
                        # schedule work
                        has_submit = True

                        if self.are_node_upstreams_successful(node):
                            # execute current node
                            executor.submit(self.execute_node, node, False)
                        else:
                            # skip current node if upstreams failed
                            executor.submit(self.execute_node, node, True)


                if has_submit:
                    rescan_with_submit_count += 1

                # Check if all is done
                if self.are_all_nodes_done():
                    logger.info("All nodes are done", SchedulerEvent())
                    break

                if total_rescan_cnt - rescan_with_submit_count > self.max_rescan_without_submit_cnt:
                    logger.error(
                        f'Max Rescan without submit count {self.max_rescan_without_submit_cnt=} is exceeded! Scheduler stopped', SchedulerEvent())
                    break

                logger.info(f'going to rescan in {self.rescan_all_nodes_in_seconds=}', SchedulerEvent())
                time.sleep(self.rescan_all_nodes_in_seconds)

    def are_node_upstreams_done(self, node: _BaseModel) -> bool:
        upstream_node_ids: Set[str] = nx.ancestors(self.digraph, id(node))

        if len(upstream_node_ids) == 0:
            # terminate
            return True
        else:
            bools = []
            for upstream_node_id in upstream_node_ids:
                bools.append(self.is_node_done(self.nodes_mapping.get(upstream_node_id)))
            return all(bools)

    def are_node_upstreams_successful(self, node: _BaseModel) -> bool:
        upstream_node_ids: Set[str] = nx.ancestors(self.digraph, id(node))

        if len(upstream_node_ids) == 0:
            # terminate
            return True
        else:
            bools = []
            for upstream_node_id in upstream_node_ids:
                bools.append(self.is_node_successful(self.nodes_mapping.get(upstream_node_id)))
            return all(bools)

    def are_all_nodes_done(self) -> bool:
        return all([self.is_node_done(node) for node in self.nodes])

    @abstractmethod
    def is_node_done(self, node: _BaseModel) -> bool:
        """
        Method which returns if a node is done or not
        Parameters
        ----------
        node

        Returns
        -------

        """
        pass

    @abstractmethod
    def is_node_successful(self, node: _BaseModel) -> bool:
        """
        Method which returns if a node is successful
        Parameters
        ----------
        node

        Returns
        -------

        """
        pass

    @abstractmethod
    def execute_node(self, node: _BaseModel, skip: bool) -> None:
        """
        Executes a node
        Parameters
        ----------
        node
        skip

        Returns
        -------

        """
        pass
