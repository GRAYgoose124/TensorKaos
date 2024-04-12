import math
import os
import arcade
import random
import networkx as nx

from ..core.utilities import setup_logging
from ..core.guiview import GuiView
from ..core.graph.builders.gamegen import (
    complex_map,
)

log = setup_logging(__name__)


def draw_chevron(start_pos, end_pos, color=arcade.color.WHITE, size=10, line_width=2):
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


# TODO: GuiView, but messes up the mouse click handling
class GraphMapView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)
        self.graph = None  # This will store the networkx graph
        self.current_node = None
        self.node_size = 15  # Radius of the node for drawing
        self.map_offset = (self.window.width // 2, self.window.height // 2)
        self.setup()

    def setup(self):
        self.graph = complex_map()

        if os.getenv("DEBUG_MAP_LAYOUT", False):
            pos = nx.get_node_attributes(self.graph, "position")
            # start with the pos gotten from self.graph.nodes(data='position')
            for _ in range(3):
                pos = nx.spring_layout(
                    self.graph,
                    pos=pos,
                    scale=2.0,
                    k=15.0,
                    iterations=50,
                    threshold=0.001,
                )
                # average the positions with the original positions
                for node in pos:
                    pos[node] = (
                        (pos[node][0] + self.graph.nodes[node]["position"][0]) / 2,
                        (pos[node][1] + self.graph.nodes[node]["position"][1]) / 2,
                    )

            nx.set_node_attributes(self.graph, pos, "position")
            print(f"Graph nodes: {list(self.graph.nodes(data=True))}")

        self.current_node = self.graph.entry_node

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AIR_SUPERIORITY_BLUE)
        return super().on_show_view()

    def on_draw(self):
        arcade.start_render()
        # TODO: Calculate scaling factors for dynamic display adjustments, if needed
        self.__draw_map_edges()
        self.__draw_map_nodes()
        self.__draw_map_labels()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            log.debug(f"Clicked at: {x}, {y}")  # Debugging click positions
            for node, data in self.graph.nodes(data=True):
                if self.__clicked_in_node(x, y, node):
                    print(f"Clicked on node: {node}")
                    if self.__can_move_to(node):
                        self.current_node = node
                        print(f"Moved to {self.current_node}")
                        break
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            log.debug(f"Right-clicked at: {x}, {y}")
            self.map_offset += (x, y)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view("game")

    def __get_offset_pos(self, pos):
        new_pos = (
            self.map_offset[0] + pos[0] * 100,
            self.map_offset[1] + pos[1] * 100,
        )
        # offset by current node position
        if self.current_node:
            current_pos = self.graph.nodes[self.current_node]["position"]
            new_pos = (
                new_pos[0] - current_pos[0] * 100,
                new_pos[1] - current_pos[1] * 100,
            )
        return new_pos

    def __draw_map_edges(self):
        for u, v in self.graph.edges():
            start_pos = self.graph.nodes[u]["position"]
            end_pos = self.graph.nodes[v]["position"]
            visual_start_pos = self.__get_offset_pos(start_pos)
            visual_end_pos = self.__get_offset_pos(end_pos)

            color = (
                arcade.color.ORANGE_RED
                if self.graph.degree(u) % 2 == 0
                else arcade.color.RASPBERRY_GLACE
            )
            arcade.draw_line(*visual_start_pos, *visual_end_pos, color, 2)
            draw_chevron(
                visual_start_pos,
                visual_end_pos,
                arcade.color.FANDANGO_PINK,
                size=10,
                line_width=2,
            )

    def __draw_map_nodes(self):
        # Draw nodes and highlight possible destinations
        for node, data in self.graph.nodes(data=True):
            position = data["position"]
            visual_position = self.__get_offset_pos(position)
            arcade.draw_circle_filled(
                *visual_position, self.node_size, arcade.color.ULTRAMARINE_BLUE
            )
            if node == self.current_node:
                arcade.draw_circle_outline(
                    *visual_position, self.node_size + 5, arcade.color.RASPBERRY_ROSE, 4
                )

    def __draw_map_labels(self):
        # Highlight neighbors (possible destinations) of the current node
        for neighbor in self.graph.neighbors(self.current_node):
            neighbor_pos = self.graph.nodes[neighbor]["position"]
            visual_neighbor_pos = self.__get_offset_pos(neighbor_pos)
            arcade.draw_circle_outline(
                *visual_neighbor_pos, self.node_size + 10, arcade.color.YELLOW, 3
            )  # Larger yellow circle

    def __clicked_in_node(self, x, y, node):
        position = self.graph.nodes[node]["position"]
        visual_position = self.__get_offset_pos(position)
        inside_x = (
            visual_position[0] - self.node_size
            <= x
            <= visual_position[0] + self.node_size
        )
        inside_y = (
            visual_position[1] - self.node_size
            <= y
            <= visual_position[1] + self.node_size
        )

        return inside_x and inside_y

    def __can_move_to(self, node):
        return node in [n for n in self.graph.neighbors(self.current_node)]

    def __clip_pos_to_window(self, pos):
        x, y = pos
        x = max(self.node_size, min(x, self.window.width - self.node_size))
        y = max(self.node_size, min(y, self.window.height - self.node_size))
        return x, y
