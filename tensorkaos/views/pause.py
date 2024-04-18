import arcade
import arcade.gui


class PauseView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)
        self.uimanager = arcade.gui.UIManager()

        self._pause_screen = self.__build_pause_screen()
        self._settings_menu = self.__build_settings_menu()
        self._gameplay_elements_dock = self.__build_gameplay_elements_dock()
        self._exit_dialog_handle = None

        self.uimanager.add(self._pause_screen)
        self.uimanager.add(self._gameplay_elements_dock)

    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)
        self.uimanager.enable()

    def on_hide_view(self):
        self.uimanager.disable()

    def on_draw(self):
        arcade.start_render()
        self.uimanager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.uimanager.remove(self._exit_dialog_handle)

            self._exit_dialog_handle = arcade.gui.UIMessageBox(
                width=300,
                height=150,
                message_text="Are you sure you want to quit?",
                buttons=("Ok", "Cancel"),
            )

            self._exit_dialog_handle._callback = self.__exit_game_dialog

            self.uimanager.add(self._exit_dialog_handle)

        return super().on_key_press(key, modifiers)

    # UI building
    def __build_pause_screen(self):
        # create buttons
        resume_button = arcade.gui.UIFlatButton(text="Resume", width=200, height=50)
        resume_button.on_click = self.__resume_game

        settings_button = arcade.gui.UIFlatButton(text="Settings", width=200, height=50)
        settings_button.on_click = lambda _: self.uimanager.add(self._settings_menu)

        restart_button = arcade.gui.UIFlatButton(text="Restart", width=200, height=50)
        restart_button.on_click = self.__restart_game

        return_to_title_button = arcade.gui.UIFlatButton(
            text="Return to Title", width=200, height=50
        )
        return_to_title_button.on_click = lambda _: self.window.show_view("title")

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200, height=50)
        quit_button.on_click = lambda _: arcade.close_window()

        # position buttons

        # build screen
        pause_screen = arcade.gui.UIBoxLayout()
        pause_screen.add(
            arcade.gui.UIAnchorWidget(
                child=arcade.gui.UITextArea(
                    text="Paused",
                    font_size=20,
                    font_name="Arial",
                    color=arcade.color.GRAY_BLUE,
                ),
                align_x=150,
                anchor_y="top",
            )
        )
        pause_screen.add(
            arcade.gui.UIAnchorWidget(
                child=arcade.gui.UIBoxLayout(
                    children=[
                        arcade.gui.UIAnchorWidget(
                            child=resume_button, anchor_x="center", anchor_y="center"
                        ),
                        arcade.gui.UIAnchorWidget(
                            child=settings_button,
                            anchor_x="center",
                            anchor_y="center",
                            align_y=-55,
                        ),
                        arcade.gui.UIAnchorWidget(
                            child=restart_button,
                            anchor_x="center",
                            anchor_y="center",
                            align_y=-110,
                        ),
                        arcade.gui.UIAnchorWidget(
                            child=return_to_title_button,
                            anchor_x="center",
                            anchor_y="center",
                            align_y=-165,
                        ),
                        arcade.gui.UIAnchorWidget(
                            child=quit_button,
                            anchor_x="center",
                            anchor_y="center",
                            align_y=-220,
                        ),
                    ]
                ),
                anchor_x="center",
                anchor_y="center",
            )
        )

        return arcade.gui.UIAnchorWidget(
            child=pause_screen, anchor_x="center", anchor_y="center"
        )

    def __build_settings_menu(self):
        menu = arcade.gui.UIBoxLayout()
        menu.add(
            arcade.gui.UITextArea(
                text="Settings",
                font_size=20,
                font_name="Arial",
                color=arcade.color.WHITE,
            )
        )

        # settings menu close button
        close_button = arcade.gui.UIFlatButton(text="Close", width=200, height=50)
        close_button.on_click = lambda _: self.uimanager.remove(menu)

        menu.add(
            arcade.gui.UIAnchorWidget(
                child=close_button, anchor_x="center", anchor_y="right"
            )
        )

        return menu

    def __build_gameplay_elements_dock(self):
        # Build the dock for gameplay elements (e.g., Map View button)
        dock = arcade.gui.UIBoxLayout(vertical=True)  # Vertical box layout for the dock

        # Map View button
        map_view_button = arcade.gui.UIFlatButton(text="Map View", width=120, height=40)
        map_view_button.on_click = self.__open_map_view

        dock.add(map_view_button)

        # Position the dock in the top left corner of the pause screen
        dock_widget = arcade.gui.UIAnchorWidget(
            anchor_x="left", anchor_y="top", child=dock
        )
        return dock_widget

    def __open_map_view(self, _):
        # Transition to the Map View
        # This assumes you have a MapView class defined elsewhere
        self.window.show_view("map")

    def __exit_game_dialog(self, button_text):
        if button_text == "Ok":
            arcade.close_window()

    def __resume_game(self, _):
        self.uimanager.remove(self._settings_menu)
        self.window.show_view("game")

    def __restart_game(self, _):
        self.window.views["game"].setup()
        self.window.show_view("game")
