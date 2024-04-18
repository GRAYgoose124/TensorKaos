import networkx as nx
import random

from ..module import GraphModule


class GameGraph(GraphModule):
    module_counter = 0  # Class variable to keep track of the number of modules created

    def new_unique_id(self):
        """Generate a new unique ID for a module."""
        unique_id = self.module_counter
        self.module_counter += 1
        return unique_id

    def create_dead_end(self):
        dead_end = GraphModule()
        entry = dead_end.add_positioned_module_node(f"Entry", (0, 0))
        one_dead = dead_end.add_positioned_module_node(f"DeadEnd", (1, 0))
        dead_end.add_edge(entry, one_dead)
        dead_end.add_edge(one_dead, entry)
        dead_end.set_entry_exit(entry, entry)
        return dead_end

    def create_broken_trident(self):
        trident = GraphModule()
        base = trident.add_positioned_module_node("Base", (0, 0))
        left_arm = trident.add_positioned_module_node("LeftArm", (2, 1))
        right_arm = trident.add_positioned_module_node("RightArm", (1, 1))
        middle_arm = trident.add_positioned_module_node(f"MiddleArm", (0, 2))
        middle_arm2 = trident.add_positioned_module_node(f"MiddleArm2", (0, 3))

        # Connect the arms to the base
        trident.add_edges_from(
            [
                (base, left_arm),
                (base, middle_arm),
                (base, right_arm),
                (middle_arm, middle_arm2),
            ]
        )
        trident.set_entry_exit(base, middle_arm2)

        return trident

    def create_c_loop(self):
        c_loop = GraphModule()
        entry = c_loop.add_positioned_module_node("Entry", (0, 0))
        loop_start = c_loop.add_positioned_module_node("LoopStart", (1, 0))
        loop_end = c_loop.add_positioned_module_node("LoopEnd", (1, 2))

        c_loop.add_edges_from(
            [(entry, loop_start), (loop_start, loop_end), (loop_end, entry)]
        )
        c_loop.set_entry_exit(entry, loop_end)

        return c_loop
