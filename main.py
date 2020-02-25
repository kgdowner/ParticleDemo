#!/usr/bin/env python

import render


# TEST SHADERS
test_vert = """
	#version 330
	in vec3 in_position;
	in vec3 in_color;

	out vec3 color;

	void main() {
		color = in_color;
		gl_Position = vec4(in_position, 1.0);
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

render.render_objects.append((test_vao, test_program))


render.render_loop()