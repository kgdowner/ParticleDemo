#!/usr/bin/env python

import render
import random


# TEST SHADERS
test_vert = """
	#version 330
	in vec3 in_position;
	in vec3 in_color;

	out vec3 color;

	uniform mat4 mvp = mat4(1.0);

	void main() {
		color = in_color;
		gl_Position = mvp * vec4(in_position, 1.0);
	}
"""

test_frag = """
	#version 330
	in vec3 color;

	out vec4 frag_color;

	void main() {
		frag_color = vec4(color, 1.0);
	}
"""


# create a test triangle & add it to the object array to be drawn
test_vao = render.create_vao([0, 0, 0, 1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 1, 0, 0, 0, 1])
test_program = render.create_program(test_vert, test_frag, ["in_position, in_color"])

square_vao = render.create_vao([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])


# particle constants
repeat_time = 5
start_position = [0, 8, 0]
max_velocity = 10
max_lifetime = 4


# add a bunch of particles to the render objects dict
for i in range(100):
	translate_scale_matrix = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
	translate_scale_matrix[3][0] = start_position[0]
	translate_scale_matrix[3][1] = start_position[1]
	translate_scale_matrix[3][2] = start_position[2]
	#rotation_matrix = [] TODO
	velocity = [
		random.uniform(-max_velocity, max_velocity),
		random.uniform(-max_velocity, max_velocity),
		random.uniform(-max_velocity, max_velocity),
	]
	lifetime = random.random() * max_lifetime

	render.render_objects.append({"vao":square_vao, "program":test_program, "matrix":translate_scale_matrix, "velocity":velocity, "lifetime":lifetime})


# update particle behavior inside the glut idle function (for now - TODO: threading?)
last_ic_time = 0
last_firework_time = 0
def ic(timestamp):
	global last_ic_time, last_firework_time

	# time since the last function call (seconds)
	delta_time = (timestamp - last_ic_time) / 1000
	system_time = (timestamp - last_firework_time) / 1000

	# update the render objects (all particles for now)
	for robject in render.render_objects:
		# add velocity from some gravity g=-10
		robject["velocity"][1] -= 10 * delta_time

		# dampening/ fake friction - TODO: more of a fixed-function based on how much velocity there is would be better
		damp_const = 0.8
		robject["velocity"][0] *= (damp_const ** delta_time)
		robject["velocity"][1] *= (damp_const ** delta_time)
		robject["velocity"][2] *= (damp_const ** delta_time)

		# update position
		robject["matrix"][3][0] += robject["velocity"][0] * delta_time
		robject["matrix"][3][1] += robject["velocity"][1] * delta_time
		robject["matrix"][3][2] += robject["velocity"][2] * delta_time

		# scale based on lifetime
		scale = max(0, (robject["lifetime"] - system_time) / robject["lifetime"])
		robject["matrix"][0][0] = scale
		robject["matrix"][1][1] = scale
		robject["matrix"][2][2] = scale

	# create a new firework event every 5 seconds
	if system_time > repeat_time:
		print("New Firework at ", timestamp/1000, " seconds")
		last_firework_time = timestamp

		# go through all the particles, reset position/scale & apply random initial velocity
		for robject in render.render_objects:
			robject["matrix"][0][0] = 1
			robject["matrix"][1][1] = 1
			robject["matrix"][2][2] = 1
			robject["matrix"][3][0] = start_position[0]
			robject["matrix"][3][1] = start_position[1]
			robject["matrix"][3][2] = start_position[2]

			robject["velocity"] = [
				random.uniform(-max_velocity, max_velocity),
				random.uniform(-max_velocity, max_velocity),
				random.uniform(-max_velocity, max_velocity),
			]

	# record the time this was run for the movement deltas
	last_ic_time = timestamp


# run the glut loops
render.idle_callback = ic
render.render_loop()