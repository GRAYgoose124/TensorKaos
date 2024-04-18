#version 430

layout(location = 0) in vec4 in_position; // Position from compute shader
layout(location = 1) in vec4 in_color; // Color

out vec4 color;

void main() {
    gl_Position = vec4(in_position.xy / screenSize * 2.0 - 1.0, 0.0, 1.0);
    gl_PointSize = in_position.w * (screenSize.y / 450.0); // Adjust point size based on screen size
    color = in_color;
}
