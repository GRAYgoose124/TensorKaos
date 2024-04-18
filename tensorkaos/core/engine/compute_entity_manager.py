import numpy as np
import arcade

class ComputeShaderManager:
    def __init__(self, context, shader_source):
        self.context = context
        self.shader = context.compute_shader(shader_source)
        self.sprite_groups = {}
        self.buffers = {}

    def add_sprite_group(self, name, sprites):
        self.sprite_groups[name] = sprites
        # Assume each sprite has a position stored as (x, y)
        positions = np.array([(s.center_x, s.center_y) for s in sprites], dtype=np.float32)
        # Create SSBO and store it in buffers dictionary
        self.buffers[name] = self.context.buffer(data=positions.tobytes())

    def update_sprites(self):
        for name, sprites in self.sprite_groups.items():
            buffer = self.buffers[name]
            # Update buffer data if necessary, e.g., sprites moved
            self.shader['positions'] = buffer
            # Run the shader
            self.shader.run(group_x=len(sprites) // 16 + 1)
            # Read back updated positions
            new_positions = np.frombuffer(buffer.read(), dtype=np.float32).reshape(-1, 2)
            for sprite, (x, y) in zip(sprites, new_positions):
                sprite.center_x, sprite.center_y = x, y

# Example of setting up the manager and adding a group of sprites
context = arcade.get_window().ctx
manager = ComputeShaderManager(context, "path/to/shader.glsl")
manager.add_sprite_group("enemies", enemy_sprites)
