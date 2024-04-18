import arcade
from arcade.gl import BufferDescription, Context, Program, Geometry
from pathlib import Path
import numpy as np

from tensorkaos.utilities.misc import get_assets_path

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
NUM_STARS = 1000


def gen_initial_data(num_entities):
    positions = np.random.uniform(-1, 1, (num_entities, 2)).astype(np.float32)
    velocities = np.zeros((num_entities, 2), dtype=np.float32)
    colors = np.random.uniform(0, 1, (num_entities, 4)).astype(np.float32)
    return np.hstack([positions, velocities, colors])


class ShaderGroup:
    def __init__(
        self,
        context,
        compute_shader_source,
        vertex_shader_source,
        num_entities,
        data_generator,
    ):
        self.context = context
        self.num_entities = num_entities

        # Prepare initial data
        initial_data = data_generator(num_entities)
        self.ssbo = context.buffer(data=initial_data.tobytes())

        # Compute shader
        self.compute_shader = context.compute_shader(source=compute_shader_source)

        # Vertex shader and rendering program
        geometry_shader_source = get_assets_path() / "shaders" / "cs_test" / "geom.glsl"
        with open(geometry_shader_source) as file:
            geometry_shader_source = file.read()

        fragment_shader_source = get_assets_path() / "shaders" / "cs_test" / "frag.glsl"
        with open(fragment_shader_source) as file:
            fragment_shader_source = file.read()

        self.program = context.program(
            vertex_shader=vertex_shader_source,
            geometry_shader=geometry_shader_source,
            fragment_shader=fragment_shader_source,
        )

        # Geometry to draw the entities
        buffer_description = BufferDescription(
            self.ssbo, "4f 4x4 4f", ["in_vertex", "in_velocity", "in_color"]
        )
        self.vao = context.geometry([buffer_description])

    def update(self):
        # Bind the ssbo to the compute shader and run it
        self.ssbo.bind_to_storage_buffer(0)
        self.compute_shader.run(group_x=self.num_entities // 256 + 1)

    def draw(self):
        # Draw entities using the rendering program
        self.vao.render(self.program)


class ComputeShaderManager:
    def __init__(self, context):
        self.context = context
        self.shader_groups = {}

    def add_shader_group(
        self,
        name,
        compute_shader_source,
        vertex_shader_source,
        num_entities,
        data_generator,
    ):
        self.shader_groups[name] = ShaderGroup(
            context=self.context,
            compute_shader_source=compute_shader_source,
            vertex_shader_source=vertex_shader_source,
            num_entities=num_entities,
            data_generator=data_generator,
        )

    def update(self):
        for group in self.shader_groups.values():
            group.update()

    def draw(self):
        for group in self.shader_groups.values():
            group.draw()


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Compute Shader Example")
    manager = ComputeShaderManager(window.ctx)

    # Load shader sources
    compute_shader_source = get_assets_path() / "shaders" / "cs_test" / "comp.glsl"
    with open(compute_shader_source) as file:
        compute_shader_source = file.read()

    vertex_shader_source = get_assets_path() / "shaders" / "cs_test" / "vert.glsl"
    with open(vertex_shader_source) as file:
        vertex_shader_source = file.read()

    # Add shader group
    manager.add_shader_group(
        name="stars",
        compute_shader_source=compute_shader_source,
        vertex_shader_source=vertex_shader_source,
        num_entities=NUM_STARS,
        data_generator=gen_initial_data,
    )

    # Main loop
    while True:
        manager.update()
        window.clear()
        manager.draw()
        window.flip()


if __name__ == "__main__":
    main()
