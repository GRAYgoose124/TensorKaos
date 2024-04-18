#version 430

layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

in vec4 color[];
out vec4 fragColor;

void main() {
    vec2 size = vec2(0.05, 0.05); // Size of the sprite
    fragColor = color[0];
    gl_Position = gl_in[0].gl_Position + vec4(-size.x, -size.y, 0.0, 0.0);
    EmitVertex();
    gl_Position = gl_in[0].gl_Position + vec4(size.x, -size.y, 0.0, 0.0);
    EmitVertex();
    gl_Position = gl_in[0].gl_Position + vec4(-size.x, size.y, 0.0, 0.0);
    EmitVertex();
    gl_Position = gl_in[0].gl_Position + vec4(size.x, size.y, 0.0, 0.0);
    EmitVertex();
    EndPrimitive();
}
