import arcade
import arcade.gui


class TitleView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)

        self.uimanager = arcade.gui.UIManager(window)

        self._title_screen = self.__build_title_screen()

        self.uimanager.add(self._title_screen)

    def on_show(self):

        arcade.set_background_color(arcade.color.BLACK)

        self.uimanager.enable()

    def on_hide_view(self):

        self.uimanager.disable()
        return super().on_hide_view()

    def on_draw(self):

        arcade.start_render()

        arcade.draw_text(
            "TensorKaos",
            self.window.width / 2,
            self.window.height / 2 + 100,
            arcade.color.WHITE,
            64,
            anchor_x="center",
        )
        arcade.draw_text(
            "on the edge of chaos, there is also order.",
            self.window.width / 2,
            self.window.height / 2 + 50,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        self.uimanager.draw()

    def __build_title_screen(self):
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200, height=50)
        start_button.on_click = lambda _: self.window.show_view("game")

        title_screen_layout = arcade.gui.UIBoxLayout()
        title_screen_layout.add(start_button)

        button_layout_anchor = arcade.gui.UIAnchorWidget(
            child=title_screen_layout, anchor_x="center_x", anchor_y="center_y"
        )

        return button_layout_anchor
