import random
import networkx as nx


def finalize_entry_exit(map, default_entry="Start_", default_exit="End_"):
    """Finalize the entry and exit nodes for the map."""
    entry = random.choice([n for n in map.nodes() if n.startswith(default_entry)])
    exit = random.choice([n for n in map.nodes() if n.startswith(default_exit)])
    map.entry_node = entry
    map.exit_node = exit
    return map


# TODO: need to fix map node positions so they're offset properly
# TODO: these need to properly assume the entry/exit node labels so that we can reference them easily in the final map
def replace_nodes(map):
    """Iteratively replace nodes in a complex map with modules."""
    for node in list(map.nodes()):
        if map.degree(node) == 1:
            c_loop = map.create_c_loop()
            map.integrate_module(node, c_loop)
        elif map.degree(node) == 2:
            # make a recursive trident by making a broken trident of broken tridents
            broken_trident = map.create_broken_trident()
            # for each node of the broken trident, integrate a broken trident
            # TODO: crashing here
            # for n in list(broken_trident.nodes()):
            #    broken_trident.replace_node_with_module(n, map.create_broken_trident())
            map.integrate_module(node, broken_trident)
        elif map.degree(node) == 3:
            broken_trident = map.create_broken_trident()
            map.integrate_module(node, broken_trident)
        elif map.degree(node) == 4:
            # go to each neighbor and create a dead end
            neighbors = list(map.neighbors(node))
            for neighbor in neighbors:
                dead_end = map.create_dead_end()
                map.integrate_module(neighbor, dead_end)
    return map


def loopback_deadends(map):
    """If a map has no outgoing edges, loop it back to an "earlier" node in the path, closer to the entry node."""
    for node in list(map.nodes()):
        if map.out_degree(node) == 0:
            for n in list(map.nodes()):
                if map.in_degree(n) > 0 or map.out_degree(n) < 2:
                    map.add_edge(node, n)
                    break
    return map


def connect_unreachable_nodes(map):
    """Connect nodes that are unreachable from the entry node."""
    print(f"Entry node: {map.entry_node}, Exit node: {map.exit_node}")
    reachable = nx.descendants(map, map.entry_node)
    reachable.add(map.entry_node)
    unreachable = set(map.nodes) - reachable
    reachable = list(reachable)

    if unreachable:
        for node in unreachable:
            if random.random() < 0.75:
                # TODO: reachable can be empty, fix
                map.add_edge(random.choice(reachable), node)
    return map


def complicate_map(graph):
    replace_nodes(graph)
    loopback_deadends(graph)
    finalize_entry_exit(graph, default_entry="Start_", default_exit="End_")
    connect_unreachable_nodes(graph)
    return graph
