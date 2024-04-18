#version 430

layout(local_size_x = 256) in;

struct Particle {
    vec4 position; // x, y, z, w (w is unused)
    vec4 velocity; // vx, vy, vz, vw (vz, vw are unused)
};

layout(std430, binding = 0) buffer Particles {
    Particle particles[];
};

uniform float deltaTime;
uniform vec2 screenSize;

void main() {
    uint idx = gl_GlobalInvocationID.x;
    if (idx >= particles.length()) return;

    Particle part = particles[idx];

    // Gravity update
    vec3 force = vec3(0.0, 0.0, 0.0);
    for (uint i = 0; i < particles.length(); i++) {
        if (i == idx) continue;
        vec3 dir = particles[i].position.xyz - part.position.xyz;
        float dist = length(dir);
        if (dist > 0.1) {
            float strength = 0.1 * (part.position.w * particles[i].position.w) / (dist * dist);
            force += strength * normalize(dir);
        }
    }

    // Update velocity and position
    part.velocity.xyz += force * deltaTime;
    part.position.xyz += part.velocity.xyz * deltaTime;

    particles[idx] = part;
}
