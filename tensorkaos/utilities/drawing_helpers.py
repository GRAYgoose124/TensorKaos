import arcade
import math


def draw_chevron(start_pos, end_pos, color=arcade.color.WHITE, size=10, line_width=2):
    """
    Draw a chevron at the midpoint of the path from start_pos to end_pos.
    """
    # Calculate the midpoint
    mid_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)

    # Calculate the angle of the line
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    angle = math.atan2(dy, dx)

    # Calculate the positions for the chevron's "V" arms
    angle_offset = math.pi / 6  # Adjust this value to change the "V" opening
    chevron_pos1 = (
        mid_pos[0] - size * math.cos(angle - angle_offset),
        mid_pos[1] - size * math.sin(angle - angle_offset),
    )
    chevron_pos2 = (
        mid_pos[0] - size * math.cos(angle + angle_offset),
        mid_pos[1] - size * math.sin(angle + angle_offset),
    )

    # Draw the chevron arms
    arcade.draw_line(
        mid_pos[0], mid_pos[1], chevron_pos1[0], chevron_pos1[1], color, line_width
    )
    arcade.draw_line(
        mid_pos[0], mid_pos[1], chevron_pos2[0], chevron_pos2[1], color, line_width
    )
