import networkx as nx
import random

from ..module import GraphModule


class GameGraph(GraphModule):
    def integrate_module(self, node, module):
        """Integrate a module at a specific node."""
        self.replace_node_with_module(node, module)
        # Additional integration logic (e.g., adjusting edges, nodes) can be handled here

    def create_dead_end(self):
        dead_end = GraphModule()
        entry = dead_end.add_positioned_module_node(f"Entry", (0, 0))
        one_dead = dead_end.add_positioned_module_node(f"DeadEnd", (1, 0))
        dead_end.add_edge(entry, one_dead)
        dead_end.add_edge(one_dead, entry)
        dead_end.set_entry_exit(entry, entry)
        return dead_end

    def create_broken_trident(self):
        trident = GraphModule()
        base = trident.add_positioned_module_node("Base", (0, 0))
        left_arm = trident.add_positioned_module_node("LeftArm", (2, 1))
        right_arm = trident.add_positioned_module_node("RightArm", (1, 1))
        middle_arm = trident.add_positioned_module_node(f"MiddleArm", (0, 2))
        middle_arm2 = trident.add_positioned_module_node(f"MiddleArm2", (0, 3))

        # Connect the arms to the base
        trident.add_edges_from(
            [
                (base, left_arm),
                (base, middle_arm),
                (base, right_arm),
                (middle_arm, middle_arm2),
            ]
        )
        trident.set_entry_exit(base, middle_arm2)

        return trident

    def create_c_loop(self):
        c_loop = GraphModule()
        entry = c_loop.add_positioned_module_node("Entry", (0, 0))
        loop_start = c_loop.add_positioned_module_node("LoopStart", (1, 0))
        loop_end = c_loop.add_positioned_module_node("LoopEnd", (1, 2))

        c_loop.add_edges_from(
            [(entry, loop_start), (loop_start, loop_end), (loop_end, entry)]
        )
        c_loop.set_entry_exit(entry, loop_end)

        return c_loop


def generate_complex_map():
    """Generate a complex map with chiral structures."""
    game_graph = GameGraph()

    # Basic setup - Add core nodes
    core_nodes = ["Start", "Mid", "End"]
    positions = [(0, 0), (3, 0), (6, 0)]  # Example positions
    for node, pos in zip(core_nodes, positions):
        game_graph.add_node(node, attr={"position": pos})

    game_graph.add_edges_from([("Start", "Mid"), ("Mid", "End")])
    game_graph.set_entry_exit("Start", "End")

    # Integrate more complex structures
    c_loop = game_graph.create_c_loop()
    game_graph.integrate_module("Start", c_loop)
    broken_trident = game_graph.create_broken_trident()
    game_graph.integrate_module("Mid", broken_trident)
    dead_end = game_graph.create_dead_end()
    game_graph.integrate_module("End", dead_end)

    return game_graph


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
    unreachable = set(map.nodes) - reachable
    reachable = list(reachable)

    if unreachable:
        for node in unreachable:
            if random.random() < 0.75:
                map.add_edge(random.choice(reachable), node)
    return map


if __name__ == "__main__":
    graph = generate_complex_map()
    print(graph.nodes(data=True))
    print(graph.edges(data=True))
    print(graph.entry_node, graph.exit_node)
    print("Graph generation successful.")

    # plot the graph
    import matplotlib.pyplot as plt

    nx.draw(graph, with_labels=True)
    plt.show()
