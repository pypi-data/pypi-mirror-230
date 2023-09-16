from typing import Any, Dict, List, Set, Tuple, Union

NodesType = List[Any]
EdgesType = Tuple[Tuple[Any, Any], ...]
ArrowType = Dict[Any, Set[Any]]


def get_parents_and_children(
    nodes: NodesType, edges: EdgesType
) -> Tuple[ArrowType, ArrowType]:
    """
    Given the nodes and edges of a digraph, produces dicts containing the
    parents and children of each node
    """
    parents = {node: set([]) for node in nodes}
    children = {node: set([]) for node in nodes}
    for a, b in edges:
        parents[b].add(a)
        children[a].add(b)
    return parents, children


def top_sort(nodes: NodesType, edges: EdgesType) -> List[Any]:
    """Topological sort of a DAG using depth first search as outlined here:
    https://en.wikipedia.org/wiki/Topological_sorting#Depth-first_search

    Parameters
    ----------
    nodes
        list of nodes
    edges
        tuple of edges, each one being a tuple (n, m) where the edge is directed
        from n to m.

    Returns
    -------
    list of nodes topoligcally sorted.
    """
    ret = []
    mark = []
    _, node_to_outgoing = get_parents_and_children(nodes, edges)

    def visit(n):
        if n in ret:
            return
        if n in mark:
            raise ValueError(
                f"Graph is not a directed acyclic graph. The cycle {exhibit_cycle(nodes, edges)} exists."
            )
        mark.append(n)
        for m in node_to_outgoing[n]:
            visit(m)
        mark.remove(n)
        ret.insert(0, n)

    while len(ret) < len(nodes):
        visit([n for n in nodes if n not in ret][0])

    return ret


def exhibit_cycle(
    nodes: NodesType, edges: EdgesType
) -> Union[NodesType, None]:
    """
    Given a directed graph containing a cycle, exhibits the cycle.
    """
    _, children = get_parents_and_children(nodes, edges)

    def explore(node, line_of_ancestors):
        if node in line_of_ancestors:
            idx = line_of_ancestors.index(node)
            return (True, line_of_ancestors[idx:] + [node])
        line_of_ancestors.append(node)
        for child in children[node]:
            cycle_exists, cycle = explore(child, line_of_ancestors)
            if cycle_exists:
                return (True, cycle)
        line_of_ancestors.pop()
        return (False, None)

    for node in nodes:
        cycle_exists, cycle = explore(node, [])
        if cycle_exists:
            return cycle
