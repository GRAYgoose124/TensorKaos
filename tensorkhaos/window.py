import arcade
import imgui

from arcade_imgui import ArcadeRenderer

from .views import *


class TensorKhaos(arcade.Window):
    def __init__(self):
        super().__init__(
            1280,
            720,
            "TensorKhaos: on the edge of chaos, there is also order.",
            gl_version=(4, 3),
            resizable=True,
        )

        imgui.create_context()
        self.renderer = ArcadeRenderer(self)
        self.view_metrics = False

        self.views = {
            "title": TitleView(),
            "game": GridGameView(),
            "pause": PauseView(),
        }

        self._last_view = None
        self.show_view("title")
        self.center_window()

    def show_view(self, view):
        if view not in self.views:
            raise ValueError(f"View '{view}' does not exist.")

        # get the key of the current view
        if self._current_view is not None and type(self._current_view) in [
            type(x) for x in self.views.values()
        ]:
            key = {v: k for k, v in self.views.items()}[self._current_view]
            self._last_view = key

        super().show_view(self.views[view])

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.show_view("pause")

    def request_close(self):
        self.close()
