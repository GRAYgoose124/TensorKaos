import arcade


class TitleView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)

        self.uimanager = arcade.gui.UIManager()

        self._title_screen = self.__build_title_screen()
        self.uimanager.add(self._title_screen)

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.uimanager.enable()

    def on_hide_view(self):
        self.uimanager.disable()

    def on_draw(self):
        arcade.start_render()
        self.uimanager.draw()

    def __build_title_screen(self):
        # Draw title "TensorKhaos" then "on the edge of chaos, there is also order."
        arcade.draw_text(
            "TensorKhaos",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            64,
            anchor_x="center",
        )
        arcade.draw_text(
            "on the edge of chaos, there is also order.",
            self.window.width / 2,
            self.window.height / 2 - 50,
            arcade.color.WHITE,
            16,
            anchor_x="center",
        )

        # Create a "Start Game" button
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200, height=50)

        # Define the action for the button click
        # Replace "game" with the actual view object or view class you want to show
        start_button.on_click = lambda _: self.window.show_view("game")

        # Create a UIBoxLayout to hold the title and button
        title_screen_layout = arcade.gui.UIBoxLayout()

        # Add a title text area
        title_screen_layout.add(
            arcade.gui.UITextArea(
                text="Title Screen",
                font_size=24,
                font_name="Arial",
                color=arcade.color.WHITE,
            )
        )

        # Add the start button
        title_screen_layout.add(start_button)

        # Wrap the layout in a UIAnchorWidget to center it on the screen
        return arcade.gui.UIAnchorWidget(
            child=title_screen_layout, anchor_x="center", anchor_y="center"
        )
