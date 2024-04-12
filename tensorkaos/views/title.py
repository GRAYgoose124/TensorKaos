import random, os

import arcade
import arcade.gui
from arcade.experimental import Shadertoy

from ..core.utilities import setup_logging, get_assets_path

log = setup_logging(__name__)


class TitleView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)
        self.uimanager = arcade.gui.UIManager(window)

        # Initialize the shader
        self._init_shader()

        # Build the title screen UI elements and add them to the UIManager
        self._title_screen = self.__build_title_screen()
        self.uimanager.add(self._title_screen)

        self.time = 0  # Initialize time for the shader

    def _init_shader(self):
        # Load the shader source code
        shader_file_path = get_assets_path() / "shaders" / "glitch_title.frag"
        with open(shader_file_path) as file:
            shader_sourcecode = file.read()

        # Create a Shadertoy instance for our shader, using the view's window size
        size = self.window.width, self.window.height
        self.shadertoy = Shadertoy(size, shader_sourcecode)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.uimanager.enable()

    def on_hide_view(self):
        self.uimanager.disable()
        return super().on_hide_view()

    def on_draw(self):
        arcade.start_render()
        # Render the Shadertoy shader effect
        self.shadertoy.render(time=self.time)

        # Custom drawing for angular boxes or other decorations
        self.draw_angular_boxes()

        # Now draw the UI elements on top of the shader effect
        self.uimanager.draw()

    def on_update(self, delta_time):
        self.time += delta_time  # Update time for the shader effect

    def __start_new_game(self, _):
        self.window.views["game"].setup()
        self.window.views["map"].setup()
        self.window.show_view("game")

    def __build_title_screen(self):
        # Create UI components for the title
        title_components = self.__create_title_components()

        # Create start button
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200, height=50)
        start_button.on_click = self.__start_new_game

        # Combine title components and start button into a vertical layout
        main_layout = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        main_layout.add(title_components)
        main_layout.add(start_button)

        # Anchor the main layout in the center of the screen
        main_layout_anchor = arcade.gui.UIAnchorWidget(
            child=main_layout, anchor_x="center_x", anchor_y="center_y"
        )

        return main_layout_anchor

    def __create_title_components(self):
        # Define title and quote labels with desired styling
        title = arcade.gui.UILabel(
            text="Tensic",
            text_color=arcade.color.BLACK,
            font_size=40,
            font_name="Arial",
        )
        # Note the added space for indentation
        title2 = arcade.gui.UILabel(
            text="    Kaos",
            text_color=arcade.color.RED,
            font_size=50,
            font_name="Arial",
        )
        quote = arcade.gui.UILabel(
            text="edging chaos; ",
            text_color=arcade.color.BLACK,
            font_size=20,
            font_name="Arial",
        )
        # Note the added space for indentation
        quote2 = arcade.gui.UILabel(
            text="order shall be founded",
            text_color=arcade.color.RED,
            font_size=15,
            font_name="Arial",
        )

        # Combine title and quotes into a layout
        title_layout = arcade.gui.UIBoxLayout(vertical=True)
        title_layout.add(title)
        title_layout.add(title2)
        title_layout.add(quote)
        title_layout.add(quote2)

        return title_layout

    def draw_angular_boxes(self, center_x=None, center_y=None, width=200, height=100):
        """Draw angular boxes as a decorative element on the screen."""
        if center_x is None:
            center_x = self.window.width // 2
        if center_y is None:
            center_y = self.window.height // 2 + 100

        # Calculate corner points for an angular box
        points = [
            (center_x - width / 2, center_y - height / 2),  # Bottom left
            (center_x + width / 2, center_y - height / 2),  # Bottom right
            (center_x + width / 2 + 20, center_y),  # Right notch
            (center_x + width / 2, center_y + height / 2),  # Top right
            (center_x - width / 2, center_y + height / 2),  # Top left
            (center_x - width / 2 - 20, center_y),  # Left notch
        ]

        # Draw the angular box
        arcade.draw_polygon_outline(points, arcade.color.WHITE, 3)
