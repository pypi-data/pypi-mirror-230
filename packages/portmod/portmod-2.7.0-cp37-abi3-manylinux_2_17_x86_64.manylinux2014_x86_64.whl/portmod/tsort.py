# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

# Necessary to allow _K, etc. to be defined in TYPE_CHECKING only
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)

if TYPE_CHECKING:
    from typeshed import SupportsDunderGT, SupportsDunderLT

    _SupportsRichComparison = Union[SupportsDunderLT, SupportsDunderGT]
    _K = TypeVar("_K", bound=_SupportsRichComparison)


class CycleException(Exception):
    """Exception indicating a graph cycle"""

    def __init__(self, message, cycle: Union[List[str], List[Tuple[str]]]):
        if isinstance(cycle[0], tuple):
            cyclestr = " -> ".join(map(lambda x: x[0], cycle))
        else:
            cyclestr = " -> ".join(cast(List[str], cycle))
        super().__init__(message + " " + cyclestr)
        self.cycle = cycle


def __min_priority(priorities: Mapping[_K, _SupportsRichComparison], nodes: Set[_K]):
    priority = "z"
    resultset = set()
    for node in nodes:
        if priorities[node] < priority:
            priority = priorities[node]
            resultset = set([node])
        elif priorities[node] == priority:
            resultset.add(node)

    return resultset


class WeightedEdge(NamedTuple):
    node: _SupportsRichComparison
    weight: _SupportsRichComparison


def tsort(
    graph: Union[
        Mapping[_K, Set[_K]],
        Mapping[_K, Set[WeightedEdge]],
    ],
    priority: Optional[Mapping[_K, _SupportsRichComparison]] = None,
):
    """
    Topologically sorts the given graph using Kahn's algorithm.

    The smallest elements appear early to ensure consistency between runs.

    args:
        graph: A dictionary mapping each vertex to a set containing its children.
               Edges must either be all weighted, or all unweighted, but None
               as a weight is equivalent to an unweighted edge and will never
               be ignored to break a cycle.
        pirority: A dictionary mapping each verted to a priority (anything which can be compared)


    returns:
        A topologically sorted list of all nodes in the graph, with each node appearing
        before its children.
    """
    _graph = dict(graph)
    unweighted = None
    L: List[_K] = []

    def find_roots():
        """Finds all root nodes without incoming edges"""
        S = {node for node in _graph.keys() if node not in L}
        nonlocal unweighted
        for edges in _graph.values():
            if unweighted:
                S -= edges
            elif unweighted is False:
                for edge, _ in edges:
                    S.discard(edge)
            elif unweighted is None:
                for value in edges:
                    if isinstance(value, WeightedEdge):
                        unweighted = False
                        S.discard(value.node)
                    else:
                        unweighted = True
                        S.discard(value)
        return S

    def push_smallest(S: Set[_K], L: List[_K]):
        # We always take the smallest value from the set, rather than an arbitrary value
        if priority is None:
            smallest = min(S)
        else:
            smallest = min(__min_priority(priority, S))

        S.remove(smallest)
        L.append(smallest)
        return smallest

    while any(edges for edges in _graph.values()):
        S = find_roots()
        while len(S) > 0:
            smallest = push_smallest(S, L)

            s_set = _graph[smallest]
            _graph[smallest] = set()
            for node in s_set:
                if unweighted:
                    if not any(node in edges for edges in _graph.values()):
                        S.add(node)
                else:
                    node, weight = node
                    if not any(
                        node in {edge for edge, _ in edges} for edges in _graph.values()
                    ):
                        S.add(node)

        if any(edges for edges in _graph.values()):
            # Graph has at least one cycle

            def invert(g):
                new: Dict[Any, Any] = {}
                for node in g:
                    for link in g[node]:
                        if not unweighted:
                            link, _ = link
                        if link in new:
                            new[link].add(node)
                        else:
                            new[link] = {node}
                return new

            def search(g, node, previous):
                if node in previous:
                    i = previous.index(node)
                    return previous[i:] + [node]

                for other in g[node]:
                    result = search(g, other, previous + [node])
                    if result:
                        return result
                return None

            # Invert graph and search for cycle
            cycle = search(
                invert(_graph), next(node for node in _graph if _graph[node]), []
            )

            if unweighted:
                raise CycleException("There is a cycle in the graph!", cycle)

            # If the edges have weights, find the smallest weight edge
            # in the cycle and remove it from the graph
            # After removal, we look for nodes without incoming edges and continue
            # adding to the sorted list
            min_edge = None
            min_weight = None
            while len(cycle) > 1:
                first_node, next_node = cycle[0], cycle[1]
                for edge, weight in _graph[next_node]:
                    if (
                        edge == first_node
                        and weight is not None
                        and (min_weight is None or weight < min_weight)
                    ):
                        min_edge = first_node, next_node
                        min_weight = weight
                del cycle[0]
            if min_edge is None:
                raise CycleException("There is a cycle in the graph!", cycle)
            else:
                _graph[min_edge[1]].remove(WeightedEdge(min_edge[0], min_weight))
    else:
        # If there are no edges
        S = find_roots()
        while len(S) > 0:
            push_smallest(S, L)

    return L
