import arcade

from ..core.guiview import GuiView, ViewMixin
from ..core.utilities import setup_logging

log = setup_logging(__name__)


class TestFeatureMixin(ViewMixin):
    def on_update(self, delta_time):
        log.debug("TestMixin.on_update")


class GridGameView(GuiView, TestFeatureMixin):
    def __init__(self, window=None):
        super().__init__(window)
        self.grid_size = (100, 100)
        self.entity_list = arcade.SpriteList()
        self.target_tick_rate = 1 / 120

    def setup(self, grid_size=(10, 10)):
        """Initialize or reset the game state."""
        self.grid_size = grid_size
        self.entity_list = arcade.SpriteList()

        ...

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def draw_content(self): ...

    def on_update(self, delta_time):
        """Update the state of the game each frame."""
        super().on_update(delta_time)
        self.step_game(delta_time)

    def add_entity(self, entity):
        """Add an entity to the grid."""
        self.entity_list.append(entity)

    def step_game(self, delta_time):
        """Update the game state each tick.

        - multiple ticks can be processed in a single frame

        """
        n = 0
        while delta_time > self.target_tick_rate:
            self.tick()
            delta_time -= self.target_tick_rate
            n += 1

        log.debug(f"Processed {n} ticks.")

    def tick(self):
        """Process a single game tick."""
        for entity in self.entity_list:
            entity.update()
