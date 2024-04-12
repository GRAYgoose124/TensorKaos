""" GuiViews provide an imgui layer on top of arcade.View. 

 Thanks to https://github.com/kfields/arcade-imgui/blob/master/imdemo/imdemo/page.py
"""

from abc import abstractmethod
import arcade
import imgui
import imgui.core
import logging

log = logging.getLogger(__name__)


class ViewMixin:
    pass


class MetaViewMixer(type):
    """Automatically calls super on the main base and all mixins classes when calling a method
    shared across bases.

    This is facilitated by the composition of each bases methods, such as when a ViewMixin provides an on_update, we now call that after the main class method.

    """

    def __new__(cls, name, bases, dct):
        method_dict = {}  # name: [method, method, ...]
        for base in bases:
            for key, value in base.__dict__.items():
                if callable(value):
                    if key not in method_dict:
                        method_dict[key] = []
                    method_dict[key].append(value)

        for key, value in dct.items():
            if callable(value):
                if key in method_dict:
                    method_dict[key].append(value)
                else:
                    method_dict[key] = [value]

        for key, methods in method_dict.items():

            def wrapper(methods):
                def wrapped(self, *args, **kwargs):
                    for method in methods:
                        method(self, *args, **kwargs)

                return wrapped

            dct[key] = wrapper(methods)

        return super().__new__(cls, name, bases, dct)


class GuiView(arcade.View, metaclass=MetaViewMixer):
    def __init__(self, window=None):
        super().__init__(window)
        self.show_gui = True
        self.widgets = []

        self.camera_sprites = arcade.Camera(
            self.window.width, self.window.height, self.window
        )
        self.camera_gui = arcade.Camera(
            self.window.width, self.window.height, self.window
        )

        self.clicked_quit = False

    def reset(self):
        pass

    def add_widget(self, widget_cls):
        self.widgets.append(widget_cls(self))

    @classmethod
    def create(self, app, name, title):
        guiview = self(app, name, title)
        guiview.reset()
        return guiview

    def on_draw(self):
        arcade.start_render()
        self.camera_sprites.use()
        self.draw_content()

        self.camera_gui.use()
        if self.show_gui:
            imgui.new_frame()

            self.draw_navbar()
            self.draw_sidebar()

            self._widget_draw()
            self.draw_gui()

            imgui.end_frame()
            imgui.render()
            self.window.renderer.render(imgui.get_draw_data())

    def on_resize(self, width, height):
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)
        return super().on_resize(width, height)

    def on_update(self, delta_time: float):
        if self.clicked_quit:
            log.info(f"Requesting Application close from GuiView: {self}")
            self.window.request_close()
        return self.update(delta_time)

    def on_quit(self):
        pass

    def on_show_view(self):
        self.show_gui = True

    def on_hide_view(self):
        self.show_gui = False

    def update(self, delta_time):
        pass

    def draw_navbar(self):
        # TODO data driven
        if imgui.begin_main_menu_bar():
            # File
            if imgui.begin_menu("File", True):
                clicked, selected_quit = imgui.menu_item("Quit", "Cmd+Q", False, True)
                self.clicked_quit = clicked or self.clicked_quit
                imgui.end_menu()

            # View
            if imgui.begin_menu("View", True):
                clicked_map, show_map = imgui.menu_item(
                    "Map", "Cmd+Shift+M", False, True
                )

                if clicked_map:
                    self.window.show_view("map")
                imgui.end_menu()

            imgui.end_main_menu_bar()

    @abstractmethod
    def draw_content(self):
        pass

    def draw_sidebar(self):
        pass

    def draw_gui(self):
        pass

    def _widget_draw(self):
        for widget in self.widgets:
            imgui.set_next_window_size(*widget.size[0], imgui.ONCE)
            imgui.set_next_window_position(
                *self.rel_to_window(*widget.size[1], widget_size=widget.size[0]),
                widget.draw_mode,
            )
            widget.draw()

    # widget helpers
    def rel_to_mouse(self, x, y):
        pos = imgui.get_cursor_screen_pos()
        x1 = pos[0] + x
        y1 = pos[1] + y
        return x1, y1

    def rel_to_window(self, x, y, widget_size=None):
        """positives are from zero, negatives are from end of window"""

        if x < 0:
            if widget_size is not None:
                x -= widget_size[0]
            x = self.window.width + x
        if y < 0:
            if widget_size is not None:
                y -= widget_size[1]
            y = self.window.height + y

        return x, y

    def percent_of(self, x, y):
        """Converts percentage of window to window coordinates

        Args:
            x (int): percentage of window width
            y (int): percentage of window height
        """
        return self.window.width * x, self.window.height * y
