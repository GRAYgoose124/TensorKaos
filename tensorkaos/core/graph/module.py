import random
import networkx as nx


class GraphModule(nx.DiGraph):
    """A GraphModule is a graph that is a node in a larger graph.
    Because a game map is uninteresting when it's just a random graph, we will use pre-defined graph structures to generate the game map.

    When we have a simple top-level graph, we can replace it's nodes with GraphModules to create a more complex graph.
    """

    module_counter = 0  # Class variable to keep track of the number of modules created

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

    def add_positioned_module_node(self, label, position, **attr):
        """Add a node with a specified position."""
        node = f"{label}_{self.new_unique_id()}"
        attr["position"] = position
        self.add_node(node, **attr)
        return node

    def new_unique_id(self):
        """Generate a new unique ID for a module."""
        unique_id = self.module_counter
        self.module_counter += 1
        return unique_id
