from .gamegen import GameGraph


def generate_base_complex():
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


if __name__ == "__main__":
    graph = generate_base_complex()
    print(graph.nodes(data=True))
    print(graph.edges(data=True))
    print(graph.entry_node, graph.exit_node)
    print("Graph generation successful.")

    # plot the graph
    import matplotlib.pyplot as plt

    nx.draw(graph, with_labels=True)
    plt.show()
