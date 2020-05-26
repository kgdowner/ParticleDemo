# handles the window and the opengl rendering inside it

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from math import *
import numpy as np

import imageio

from vector_util import *



# settings
display_mode	= GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH
window_title	= "Particle Demo"
window_width	= 1280
window_height	= 720
window_x		= 0
window_y		= 0
fullscreen		= False

field_of_view_h	= 90
field_of_view_v	= degrees(2 * atan(tan(radians(field_of_view_h) / 2) * window_height / window_width))
clip_dist_near	= 0.1
clip_dist_far	= 100
clear_color		= [0, 0, 0, 0]
clear_color		= [0.15, 0.15, 0.15, 1]
clear_depth		= 1.0

sensitivity	= 4		# 1 = direct translation from pixels to FOV angle moved
move_speed	= 8		# In units / second

move_forward	= ord('w')
move_backward	= ord('s')
move_left		= ord('a')
move_right		= ord('d')
move_up			= ord(' ')
move_down		= ord('c')
#pan_camera		= GLUT_RIGHT_BUTTON

exit_key		= 27  # ASCII escape


# globals
projection_matrix = None
camera_translation_matrix = [[1, 0, 0, 0], [0, 1, 0, 4], [0, 0, 1, -20], [0, 0, 0, 1]]
camera_basis = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]]

pressed_keys = {}
pressed_mouse = {}

render_objects = []

idle_callback = None



# object functions
#gluPerspective(field_of_view_v, float(window_width)/float(window_height), clip_dist_near, clip_dist_far)
def create_projection_matrix(vertical_fov, width, height, clip_near, clip_far):
	theta = radians(vertical_fov)/2

	n = clip_near
	f = clip_far
	t = clip_near * tan(theta)
	b = -t
	r = t * width / height
	l = -r

	return [
		[n/r,   0,            0,            0],
		[  0, n/t,            0,            0],
		[  0,   0, -(f+n)/(f-n), -2*n*f/(f-n)],
		[  0,   0,           -1,            0],
	]


def create_vbo(data_list, buffer_type):
	data = np.array(data_list, dtype=np.float32)

	index = glGenBuffers(1)
	glBindBuffer(buffer_type, index)
	glBufferData(buffer_type, data.nbytes, data, GL_STATIC_DRAW)

	return index


def create_tbo(image_path, buffer_type):
	data = imageio.imread(image_path)
	height, width, _ = data.shape

	index = glGenTextures(1)
	glBindTexture(buffer_type, index)
	glTexImage2D(buffer_type, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

	glTexParameteri(buffer_type, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	glTexParameteri(buffer_type, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

	return index


def create_vao(points, colors, uv_coordinates):
	# create vertex buffer objects
	index_points = create_vbo(points, GL_ARRAY_BUFFER)
	index_colors = create_vbo(colors, GL_ARRAY_BUFFER)
	index_uv	 = create_vbo(uv_coordinates, GL_ARRAY_BUFFER)

	# create vertex array object & add vbos
	index_vao = glGenVertexArrays(1)
	glBindVertexArray(index_vao)

	glBindBuffer(GL_ARRAY_BUFFER, index_points)
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

	glBindBuffer(GL_ARRAY_BUFFER, index_colors)
	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

	glBindBuffer(GL_ARRAY_BUFFER, index_uv)
	glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)

	# enable the vbo's in the vao
	glEnableVertexAttribArray(0)
	glEnableVertexAttribArray(1)
	glEnableVertexAttribArray(2)

	return index_vao


def create_shader(shader_text, shader_type):
	shader = glCreateShader(shader_type)
	glShaderSource(shader, shader_text)
	glCompileShader(shader)

	return shader


def create_program(vert_shader, frag_shader, attributes):
	program = glCreateProgram()

	glAttachShader(program, create_shader(vert_shader, GL_VERTEX_SHADER))
	glAttachShader(program, create_shader(frag_shader, GL_FRAGMENT_SHADER))

	index = 0
	for attrib in attributes:
		glBindAttribLocation(program, index, attrib)
		index += 1

	glLinkProgram(program)

	return program



# helper functions
def render_loop():
	glutMainLoop()



# callbacks
def keyboard_func(key, x, y):
	global pressed_keys

	# convert this key to ascii decimal code
	ascii_key = ord(key.decode())

	# record the time this key was pressed down
	pressed_keys[ascii_key] = glutGet(GLUT_ELAPSED_TIME)


def keyboard_up_func(key, x, y):
	global pressed_keys

	# convert this key to ascii decimal code
	ascii_key = ord(key.decode())

	# stopped pressing this key
	if pressed_keys[ascii_key]:
		pressed_keys.pop(ascii_key)


def mouse_func(button, state, x, y):
	global pressed_mouse

	# record mouse cursor position & initial movement delta (0) in pressed_mouse
	if state == GLUT_DOWN:
		pressed_mouse[button] = [x, y, 0, 0]
	else:
		pressed_mouse.pop(button)


def motion_func(x, y):
	global pressed_mouse

	# update mouse movement delta and cursor position as the mouse is moved
	for button in pressed_mouse:
		pressed_mouse[button][2] += (x - pressed_mouse[button][0])
		pressed_mouse[button][3] += (y - pressed_mouse[button][1])
		pressed_mouse[button][0] = x
		pressed_mouse[button][1] = y


def display_func():
	# clear screen and reset transform matrix
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	# calculate the view matrix
	camera_rotation_matrix = np.linalg.solve(np.eye(4), camera_basis).T

	ctmr = np.array(camera_translation_matrix)
	ctmr[0][3] *= -1
	ctmr[1][3] *= -1
	ctmr[2][3] *= -1
	ctmr = ctmr.T

	view_matrix = np.dot(ctmr, camera_rotation_matrix)

	# calculate view-projection matrix
	vp = np.dot(view_matrix, projection_matrix)

	# camera / object transformations
	glLoadMatrixf(vp)


	# 3D Coordinates Indicator
	glBegin(GL_LINES)

	# glColor3f(1.0, 0.0, 0.0)
	# glVertex3f( 2.0, 0.0, 0.0)
	# glVertex3f(-2.0, 0.0, 0.0)

	glColor3f(0.0, 1.0, 0.0)
	glVertex3f(0.0,  2.0, 0.0)
	glVertex3f(0.0, -2.0, 0.0)

	# glColor3f(0.0, 0.0, 1.0)
	# glVertex3f(0.0, 0.0,  2.0)
	# glVertex3f(0.0, 0.0, -2.0)

	glEnd()

	# 2D Coordinate Grid on XZ axis
	grid_side_length = 10
	glBegin(GL_LINES)

	# z-axis lines
	for i in range(grid_side_length+1):
		if i == grid_side_length/2:
			glColor3f(0.0, 0.0, 1.0)
		else:
			glColor3f(1.0, 1.0, 1.0)

		glVertex3f(i - grid_side_length/2, 0.0, -grid_side_length/2)
		glVertex3f(i - grid_side_length/2, 0.0,  grid_side_length/2)

	# x-axis lines
	for i in range(grid_side_length+1):
		if i == grid_side_length/2:
			glColor3f(1.0, 0.0, 0.0)
		else:
			glColor3f(1.0, 1.0, 1.0)

		glVertex3f(-grid_side_length/2, 0.0, i - grid_side_length/2)
		glVertex3f( grid_side_length/2, 0.0, i - grid_side_length/2)

	glEnd()


	# draw objects passed to the render_objects array
	glActiveTexture(GL_TEXTURE0)
	glBindTexture(GL_TEXTURE_2D, 1)
	for robj in render_objects:
		glUseProgram(robj["program"])

		# if there's a model matrix in the render object, fold it into the mvp, otherwise just use vp
		mvp = vp
		if "matrix" in robj:
			mvp = np.dot(robj["matrix"], vp)

		# set the modelview matrix uniform
		mvp_location = glGetUniformLocation(robj["program"], "mvp")
		if mvp_location != -1:
			glUniformMatrix4fv(mvp_location, 1, GL_FALSE, mvp)

		# set the texture location
		tex_location = glGetUniformLocation(robj["program"], "texture_sample")
		if tex_location != -1:
			glUniform1i(tex_location, 0)

		# conditionally disable depth buffering
		if "depth" in robj:# and robj["depth"] == False:
			glDisable(GL_DEPTH_TEST)

		# draw this array
		glBindVertexArray(robj["vao"])

		glBindBuffer(GL_ARRAY_BUFFER, glGetVertexAttribiv(0, GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING)[0])
		vbo_size = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)
		triangle_count = vbo_size // 12  # it seems the vbo stores a vector of size 4 regardless of a vao attrib size of 3, so /4, then /3 for # tris

		glDrawArrays(GL_TRIANGLES, 0, triangle_count)

		# re-enable the depth buffer
		glEnable(GL_DEPTH_TEST)


	glUseProgram(0)


	glutSwapBuffers()


def idle_func():
	global pressed_keys, pressed_mouse, camera_rotation, idle_callback

	# exit condition
	if exit_key in pressed_keys:
		sys.exit()

	# get time
	current_time = glutGet(GLUT_ELAPSED_TIME)

	# camera translation
	direction = [0, 0, 0]

	if move_forward in pressed_keys:
		delta = current_time - pressed_keys[move_forward]
		direction = add_vectors(mult_vector(-move_speed * delta / 1000, camera_basis[2][:3]), direction)
		pressed_keys[move_forward] = current_time

	if move_backward in pressed_keys:
		delta = current_time - pressed_keys[move_backward]
		direction = add_vectors(mult_vector(move_speed * delta / 1000, camera_basis[2][:3]), direction)
		pressed_keys[move_backward] = current_time

	if move_left in pressed_keys:
		delta = current_time - pressed_keys[move_left]
		direction = add_vectors(mult_vector(-move_speed * delta / 1000, camera_basis[0][:3]), direction)
		pressed_keys[move_left] = current_time

	if move_right in pressed_keys:
		delta = current_time - pressed_keys[move_right]
		direction = add_vectors(mult_vector(move_speed * delta / 1000, camera_basis[0][:3]), direction)
		pressed_keys[move_right] = current_time

	if move_up in pressed_keys:
		delta = current_time - pressed_keys[move_up]
		direction = add_vectors(mult_vector(move_speed * delta / 1000, camera_basis[1][:3]), direction)
		pressed_keys[move_up] = current_time

	if move_down in pressed_keys:
		delta = current_time - pressed_keys[move_down]
		direction = add_vectors(mult_vector(-move_speed * delta / 1000, camera_basis[1][:3]), direction)
		pressed_keys[move_down] = current_time

	camera_translation_matrix[0][3] += direction[0]
	camera_translation_matrix[1][3] += direction[1]
	camera_translation_matrix[2][3] += direction[2]

	# camera rotation - TODO: way of selecting keypress/other mouse button in settings?
	if GLUT_RIGHT_BUTTON in pressed_mouse:
		degrees_x = field_of_view_h * pressed_mouse[GLUT_RIGHT_BUTTON][2] / window_width
		degrees_y = field_of_view_v * pressed_mouse[GLUT_RIGHT_BUTTON][3] / window_height

		# calculate new forward, right, and up directions
		new_rd = roty(camera_basis[0][:3], sensitivity * degrees_x)
		new_ud = rot_vec_axis_angle(camera_basis[1][:3], camera_basis[0][:3], sensitivity * degrees_y)
		new_ud = roty(new_ud, sensitivity * degrees_x)
		new_fd = rot_vec_axis_angle(camera_basis[2][:3], camera_basis[0][:3], sensitivity * degrees_y)
		new_fd = roty(new_fd, sensitivity * degrees_x)

		# assign the new directions
		camera_basis[0][0] = new_rd[0]
		camera_basis[0][1] = new_rd[1]
		camera_basis[0][2] = new_rd[2]
		camera_basis[1][0] = new_ud[0]
		camera_basis[1][1] = new_ud[1]
		camera_basis[1][2] = new_ud[2]
		camera_basis[2][0] = new_fd[0]
		camera_basis[2][1] = new_fd[1]
		camera_basis[2][2] = new_fd[2]

		# reset mouse deltas
		pressed_mouse[GLUT_RIGHT_BUTTON][2] = 0
		pressed_mouse[GLUT_RIGHT_BUTTON][3] = 0

	# callback function for running particle code
	if idle_callback:
		idle_callback(current_time)

	# tell glut to re-run the display function
	glutPostRedisplay()



# set up glut window
glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(window_width, window_height)
glutInitWindowPosition(window_x, window_y)

window = glutCreateWindow(window_title)

if fullscreen:
	glutFullScreen()

# register glut callbacks
glutIgnoreKeyRepeat(1)

glutKeyboardFunc(keyboard_func)
glutKeyboardUpFunc(keyboard_up_func)
glutMouseFunc(mouse_func)
glutMotionFunc(motion_func)

glutDisplayFunc(display_func)
glutIdleFunc(idle_func)


# initial opengl settings
glClearColor(clear_color[0], clear_color[1], clear_color[2], clear_color[3])
glClearDepth(clear_depth)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#glDepthFunc(GL_LESS)  # default
#glShadeModel(GL_SMOOTH)  # default
#glShadeModel(GL_FLAT)


# set up projection matrix
projection_matrix = create_projection_matrix(field_of_view_v, window_width, window_height, clip_dist_near, clip_dist_far)
projection_matrix = np.array(projection_matrix).T