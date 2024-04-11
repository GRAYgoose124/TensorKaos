import math
import arcade
import random
import networkx as nx

from ..core.graph.builders.gamegen import (
    generate_complex_map,
    replace_nodes,
    loopback_deadends,
    connect_unreachable_nodes,
)


class GraphMapView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)
        self.graph = None  # This will store the networkx graph
        self.current_node = None
        self.node_size = 15  # Radius of the node for drawing
        self.map_offset = (150, 50)  # Offset for drawing the map
        self.setup_graph()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AIR_SUPERIORITY_BLUE)
        return super().on_show_view()

    def setup(self):
        self.setup_graph()

    def setup_graph(self):
        self.graph = replace_nodes(generate_complex_map())
        self.graph = loopback_deadends(self.graph)
        self.graph.entry_node = random.choice(list(self.graph.nodes))
        self.graph.exit_node = random.choice(list(self.graph.nodes))
        self.graph = connect_unreachable_nodes(self.graph)

        # Find the "earliest" node from the standpoint of the directed graph, we can look at module.entry_nodes
        print(f"Entry nodes: {list(self.graph.nodes(data=True))}")

        self.current_node = self.graph.entry_node

    def on_draw(self):
        arcade.start_render()
        # Calculate scaling factors for dynamic display adjustments, if needed

        # Draw edges with chevrons
        for u, v in self.graph.edges():
            start_pos = self.graph.nodes[u]["position"]
            end_pos = self.graph.nodes[v]["position"]
            visual_start_pos = (
                self.map_offset[0] + start_pos[0] * 100,
                self.map_offset[1] + start_pos[1] * 100,
            )
            visual_end_pos = (
                self.map_offset[0] + end_pos[0] * 100,
                self.map_offset[1] + end_pos[1] * 100,
            )

            color = (
                arcade.color.ORANGE_RED
                if self.graph.degree(u) % 2 == 0
                else arcade.color.RASPBERRY_GLACE
            )
            arcade.draw_line(*visual_start_pos, *visual_end_pos, color, 2)
            self.draw_chevron(
                visual_start_pos,
                visual_end_pos,
                arcade.color.FANDANGO_PINK,
                size=10,
                line_width=2,
            )

        # Draw nodes and highlight possible destinations
        for node, data in self.graph.nodes(data=True):
            position = data["position"]
            visual_position = (
                self.map_offset[0] + position[0] * 100,
                self.map_offset[1] + position[1] * 100,
            )
            arcade.draw_circle_filled(
                *visual_position, self.node_size, arcade.color.ULTRAMARINE_BLUE
            )
            if node == self.current_node:
                arcade.draw_circle_outline(
                    *visual_position, self.node_size + 5, arcade.color.RASPBERRY_ROSE, 4
                )

        # Highlight neighbors (possible destinations) of the current node
        for neighbor in self.graph.neighbors(self.current_node):
            neighbor_pos = self.graph.nodes[neighbor]["position"]
            visual_neighbor_pos = (
                self.map_offset[0] + neighbor_pos[0] * 100,
                self.map_offset[1] + neighbor_pos[1] * 100,
            )
            arcade.draw_circle_outline(
                *visual_neighbor_pos, self.node_size + 10, arcade.color.YELLOW, 3
            )  # Larger yellow circle

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            print(f"Clicked at: {x}, {y}")  # Debugging click positions
            for node, data in self.graph.nodes(data=True):
                position = data["position"]
                visual_position = (
                    self.map_offset[0] + position[0] * 100,
                    self.map_offset[1] + position[1] * 100,
                )
                if (
                    visual_position[0] - self.node_size
                    <= x
                    <= visual_position[0] + self.node_size
                ) and (
                    visual_position[1] - self.node_size
                    <= y
                    <= visual_position[1] + self.node_size
                ):
                    print(f"Attempting to move to: {node}")  # Debugging attempted moves
                    print(
                        f"Neighbors of {self.current_node}: {list(self.graph.neighbors(self.current_node))}"
                    )  # Debugging
                    if (
                        node in [n for n in self.graph.neighbors(self.current_node)]
                        or node == self.current_node
                    ):
                        self.current_node = node
                        print(f"Moved to {self.current_node}")
                        break

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view("game")

    def draw_chevron(
        self, start_pos, end_pos, color=arcade.color.WHITE, size=10, line_width=2
    ):
        """
        Draw a chevron at the midpoint of the path from start_pos to end_pos.
        """
        # Calculate the midpoint
        mid_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)

        # Calculate the angle of the line
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        angle = math.atan2(dy, dx)

        # Calculate the positions for the chevron's "V" arms
        angle_offset = math.pi / 6  # Adjust this value to change the "V" opening
        chevron_pos1 = (
            mid_pos[0] - size * math.cos(angle - angle_offset),
            mid_pos[1] - size * math.sin(angle - angle_offset),
        )
        chevron_pos2 = (
            mid_pos[0] - size * math.cos(angle + angle_offset),
            mid_pos[1] - size * math.sin(angle + angle_offset),
        )

        # Draw the chevron arms
        arcade.draw_line(
            mid_pos[0], mid_pos[1], chevron_pos1[0], chevron_pos1[1], color, line_width
        )
        arcade.draw_line(
            mid_pos[0], mid_pos[1], chevron_pos2[0], chevron_pos2[1], color, line_width
        )
