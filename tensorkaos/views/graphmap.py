import math
import os
import arcade
import random
import networkx as nx

from ..utilities.misc import setup_logging
from ..utilities.drawing_helpers import draw_chevron
from ..core.map.builders.helpers import complicate_map
from ..core.map.builders.generators import generate_base_complex

from ..core.guiview import GuiView

log = setup_logging(__name__)


# TODO: GuiView, but messes up the mouse click handling
class GraphMapView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)
        self.graph = None  # This will store the networkx graph
        self.current_node = None
        self.node_size = 15  # Radius of the node for drawing
        self.map_offset = (self.window.width // 2, self.window.height // 2)
        self.setup()

    def __set_debug_layout(self):
        pos = nx.get_node_attributes(self.graph, "position")
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
        log.debug(f"Graph nodes: {list(self.graph.nodes(data=True))}")

    def setup(self):
        self.graph = complicate_map(generate_base_complex())

        if os.getenv("DEBUG_MAP_LAYOUT", False):
            self.__set_debug_layout()

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
                if self.__clicked_in_node(x, y, node) and node != self.current_node:
                    log.debug(f"Clicked on node: {node}")
                    if self.__can_move_to(node):
                        self.current_node = node
                        log.debug(f"Moved to {self.current_node}")
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

        # clip to window
        new_pos = self.__clip_pos_to_window(new_pos)
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
            # also highight neighbors of neighbors with two yellow circles
            for nn in self.graph.neighbors(neighbor):
                nn_pos = self.graph.nodes[nn]["position"]
                visual_nn_pos = self.__get_offset_pos(nn_pos)
                arcade.draw_circle_outline(
                    *visual_nn_pos, self.node_size + 15, arcade.color.OCEAN_BOAT_BLUE, 3
                )

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
