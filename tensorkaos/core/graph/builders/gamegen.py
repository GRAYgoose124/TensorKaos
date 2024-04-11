import random
import networkx as nx


class GraphModule(nx.DiGraph):
    """A GraphModule is a graph that is a node in a larger graph.
    Because a game map is uninteresting when it's just a random graph, we will use pre-defined graph structures to generate the game map.

    When we have a simple top-level graph, we can replace it's nodes with GraphModules to create a more complex graph.
    """

    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.entry_node = None
        self.exit_node = None

    def set_entry_exit(self, entry, exit):
        """Set the entry and exit nodes for the module."""
        if entry in self.nodes and exit in self.nodes:
            self.entry_node = entry
            self.exit_node = exit
        else:
            raise ValueError("Entry/Exit nodes must be part of the module.")

    def replace_node_with_module(self, node, module):
        """Replace a node with a module, offsetting module positions by the original node's position."""
        if not module.entry_node or not module.exit_node:
            raise ValueError("Module must have defined entry and exit nodes.")

        # Check if the node exists and get its position
        if node not in self:
            raise KeyError(f"Node '{node}' not found in the graph.")
        original_pos = self.nodes[node].get("position", (0, 0))

        in_edges = list(self.in_edges(node, data=True))
        out_edges = list(self.out_edges(node, data=True))
        self.remove_node(node)

        # Offset module's nodes positions based on the original node's position and add them
        for n, attrs in module.nodes(data=True):

            module_pos = attrs.get("position", (0, 0))
            offset_pos = (
                original_pos[0] + module_pos[0],
                original_pos[1] + module_pos[1],
            )
            attrs["position"] = offset_pos
            self.add_node(n, **attrs)  # Add updated position to attrs

        # update the edges in the main graph from the module
        for u, v, attrs in module.edges(data=True):
            u_offset = (
                original_pos[0] + module.nodes[u]["position"][0],
                original_pos[1] + module.nodes[u]["position"][1],
            )
            v_offset = (
                original_pos[0] + module.nodes[v]["position"][0],
                original_pos[1] + module.nodes[v]["position"][1],
            )
            attrs["position"] = (u_offset, v_offset)
            self.add_edge(u, v, **attrs)

        # Reconnect edges to the entry and exit nodes of the module
        for u, v, attrs in in_edges:
            self.add_edge(u, module.entry_node, **attrs)
        for u, v, attrs in out_edges:
            self.add_edge(module.exit_node, v, **attrs)

    def add_node_with_position(self, node, position, **attr):
        """Add a node with a specified position."""
        attr["position"] = position
        self.add_node(node, **attr)


class GameGraph(GraphModule):
    module_counter = 0  # Class variable to keep track of the number of modules created

    def integrate_module(self, node, module):
        """Integrate a module at a specific node."""
        self.replace_node_with_module(node, module)
        # Additional integration logic (e.g., adjusting edges, nodes) can be handled here

    def new_unique_id(self):
        """Generate a new unique ID for a module."""
        unique_id = GameGraph.module_counter
        GameGraph.module_counter += 1
        return unique_id

    def create_dead_end(self):
        unique_id = self.new_unique_id()

        dead_end = GraphModule()
        # Append the unique_id to each node name to ensure uniqueness
        dead_end.add_node_with_position(f"Entry_{unique_id}", (0, 0))
        dead_end.add_node_with_position(f"DeadEnd_{unique_id}", (1, 0))
        dead_end.add_edge(f"Entry_{unique_id}", f"DeadEnd_{unique_id}")
        dead_end.set_entry_exit(f"Entry_{unique_id}", f"DeadEnd_{unique_id}")
        return dead_end

    def create_broken_trident(self):
        unique_id = self.new_unique_id()
        trident = GraphModule()
        base = f"Base_{unique_id}"
        left_arm = f"LeftArm_{unique_id}"
        right_arm = f"RightArm_{unique_id}"
        middle_arm = f"MiddleArm_{unique_id}"
        middle_arm2 = f"MiddleArm2_{unique_id}"

        # Adding nodes with unique identifiers
        trident.add_node_with_position(base, (0, 0))
        trident.add_node_with_position(left_arm, (-1, 1))
        trident.add_node_with_position(right_arm, (1, 1))
        trident.add_node_with_position(middle_arm, (0, 2))
        trident.add_node_with_position(middle_arm2, (0, 3))

        # Connect the arms to the base
        trident.add_edges_from(
            [
                (base, left_arm),
                (base, middle_arm),
                (base, right_arm),
                (middle_arm, middle_arm2),
            ]
        )
        trident.set_entry_exit(
            base, middle_arm2
        )  # Assuming Base is both entry and exit for simplicity

        return trident

    def create_c_loop(self):
        unique_id = self.new_unique_id()
        entry = f"Entry_{unique_id}"
        loop_start = f"LoopStart_{unique_id}"
        loop_end = f"LoopEnd_{unique_id}"

        c_loop = GraphModule()
        c_loop.add_node_with_position(entry, (0, 0))
        c_loop.add_node_with_position(loop_start, (1, 0))
        c_loop.add_node_with_position(loop_end, (1, 2))

        # Connecting the nodes to form a C loop
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
        game_graph.add_node_with_position(node, pos)

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


def loopback_deadends(map, entry_node):
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
