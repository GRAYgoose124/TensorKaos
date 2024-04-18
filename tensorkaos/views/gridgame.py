import numpy as np
import random
import arcade
from arcade.gl import BufferDescription

from ..utilities.misc import get_assets_path, setup_logging

log = setup_logging(__name__)


class ShaderGroup:
    def __init__(self, context, shader_source, buffer_descriptions):
        self.context = context
        self.shader = context.compute_shader(source=shader_source)
        self.sprites = arcade.SpriteList()
        self.buffer_descriptions = (
            buffer_descriptions  # This is now a list of BufferDescription
        )

    def add_sprites(self, sprites):
        self.sprites.extend(sprites)
        # Since buffer setup is already handled during initialization, you may not need to do it here again

    def update_sprites(self):
        # Update data in buffers if necessary before running the shader
        # Bind buffers and run the shader
        self.shader.run(group_x=len(self.sprites) // 256 + 1)

    def draw(self):
        self.sprites.draw()


class ComputeShaderManager:
    def __init__(self, context):
        self.context = context
        self.shader_groups = {}

    def create_shader_group(self, name, shader_source, buffer_descriptions):
        self.shader_groups[name] = ShaderGroup(
            self.context, shader_source, buffer_descriptions
        )

    def add_sprites_to_group(self, name, sprites):
        if name in self.shader_groups:
            self.shader_groups[name].add_sprites(sprites)

    def on_update(self):
        for group in self.shader_groups.values():
            group.update_sprites()

    def draw(self):
        for group in self.shader_groups.values():
            group.draw()


class BoidSwarmEntity(arcade.Sprite):
    def __init__(
        self,
        image_file,
        scale,
        shader_group_name,
        target=None,
        manager=None,
        *args,
        **kwargs
    ):
        super().__init__(image_file, scale, *args, **kwargs)
        self.target = target

    def update(self):
        # Update logic now handled by ComputeShaderManager and its shaders
        # The 'update' method could be used for other non-GPU-related updates if necessary
        pass


class GridGameView(arcade.View):
    def __init__(self, window=None):
        super().__init__(window)
        self.manager = ComputeShaderManager(self.window.ctx)

        cshader_path = get_assets_path() / "shaders" / "compute" / "swarm_target.glsl"
        with open(cshader_path) as file:
            shader_source = file.read()

        # Combining position and angle data in one buffer
        buffer = self.manager.context.buffer(
            reserve=100 * (8 + 4)
        )  # Reserve for 2 floats for pos and 1 float for angle per entity
        buffer_description = BufferDescription(
            buffer=buffer,
            formats="2f 1f",  # vec2 for position, float for angle
            attributes=["in_pos", "in_angle"],  # Attribute names in the shader
            instanced=True,
        )

        # Pass the single BufferDescription
        self.manager.create_shader_group("boids", shader_source, [buffer_description])
        self.setup()

    def setup(self, grid_size=(10, 10)):
        self.menu_area_height = 100
        self.grid_size = grid_size
        self.game_over = False

        # create a swarm of entities
        target = arcade.SpriteCircle(10, arcade.color.RED, 10)
        target.center_x = self.window.width // 2
        target.center_y = self.window.height // 2
        self.target = target

        positions = []
        angles = []

        # Create and add boids to the manager
        for _ in range(100):
            x = random.uniform(0, self.window.width)
            y = random.uniform(0, self.window.height)
            angle = random.uniform(0, 360)
            positions.extend([x, y])
            angles.append(angle)

            boid = BoidSwarmEntity(
                ":resources:images/enemies/slimeBlue.png",
                0.1,
                "boids",
                target=self.target,
                manager=self.manager,
            )
            self.manager.add_sprites_to_group("boids", [boid])

        # Populate the buffer with initial data
        buffer = self.manager.shader_groups["boids"].buffer_descriptions[0].buffer
        buffer.write(np.array(positions + angles, dtype=np.float32).tobytes())

    def on_draw(self):
        arcade.start_render()
        # Define the game area (excluding the menu area)
        game_area_height = self.window.height - self.menu_area_height

        # Draw the game area
        self._draw_game_area()
        # Optionally, draw the menu area
        self._draw_menu_area()

    def _draw_game_area(self):
        # Example: Fill the game area with a different color
        arcade.draw_lrtb_rectangle_filled(
            0,
            self.window.width,
            self.window.height,
            self.menu_area_height,
            arcade.color.MAGENTA_HAZE,
        )

        self.manager.draw()
        self.target.draw()

    def _draw_menu_area(self):
        # Example: Fill the menu area with a different color
        arcade.draw_lrtb_rectangle_filled(
            0, self.window.width, self.menu_area_height, 0, arcade.color.ASH_GREY
        )
        # Add menu drawing logic here

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_update(self, delta_time):
        """Update the state of the game each frame."""
        super().on_update(delta_time)
        self.manager.on_update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view("pause")
