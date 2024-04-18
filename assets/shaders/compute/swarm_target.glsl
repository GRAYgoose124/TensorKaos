#version 430

layout(local_size_x = 256) in;

// Buffer for entity positions
layout(std430, binding = 0) buffer PositionBuffer {
    vec2 in_pos[];
};
layout(std430, binding = 1) buffer AngleBuffer {
    float in_angles[];
};


// Uniforms
uniform vec2 targetPos;  // Target position
uniform float deltaTime; // Time step

void main() {
    uint idx = gl_GlobalInvocationID.x;

    if (idx >= in_pos.length()) {
        return;
    }

    // Current position of the entity
    vec2 pos = in_pos[idx].xy;

    // Calculate the angle to the target
    float angle = atan(targetPos.y - pos.y, targetPos.x - pos.x);

    // Update position based on the angle
    pos.x += cos(angle) * 2.0 * deltaTime;
    pos.y += sin(angle) * 2.0 * deltaTime;

    // Write the updated position back to the buffer
    in_pos[idx].xy = pos;
}
