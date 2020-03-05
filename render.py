# handles the window and the opengl rendering inside it

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from math import *
import numpy as np

from vector_util import *



# settings
display_mode	= GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH
window_title	= "Particle Demo"
window_width	= 1024
window_height	= 768
window_x		= 2300
window_y		= 600

field_of_view_h	= 90
field_of_view_v	= degrees(2 * atan(tan(field_of_view_h / 2) * window_height / window_width))
clip_dist_near	= 0.1
clip_dist_far	= 100
clear_color		= [0, 0, 0, 0]
clear_depth		= 1.0

sensitivity	= 4		# 1 = direct translation from pixels to FOV angle moved
move_speed	= 8		# In units / second

move_forward	= ord('w')
move_backward	= ord('s')
move_left		= ord('a')
move_right		= ord('d')
move_up			= ord(' ')
move_down		= ord('c')
#pan_camera		=  # TODO: move mouse movement to glut idle func


# globals
camera_position	= [0, 0, 6]
camera_rotation	= [0, 0, 0]

pressed_keys = {}
pressed_mouse = {}

render_objects = []



# object functions
def create_vbo(data_list, buffer_type):
	data = np.array(data_list, dtype=np.float32)

	index = glGenBuffers(1)
	glBindBuffer(buffer_type, index)
	glBufferData(buffer_type, data.nbytes, data, GL_STATIC_DRAW)

	return index


def create_vao(points, colors):
	# create vertex buffer objects
	index_points = create_vbo(points, GL_ARRAY_BUFFER)
	index_colors = create_vbo(colors, GL_ARRAY_BUFFER)

	# create vertex array object & add vbos
	index_vao = glGenVertexArrays(1)
	glBindVertexArray(index_vao)

	glBindBuffer(GL_ARRAY_BUFFER, index_points)
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

	glBindBuffer(GL_ARRAY_BUFFER, index_colors)
	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

	# enable the vbo's in the vao
	glEnableVertexAttribArray(0)
	glEnableVertexAttribArray(1)

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


def move_camera(axis_vector, time_delta):
	global camera_position

	direction = mult_vector(move_speed * time_delta / 1000, axis_vector)
	direction = rot3(direction, camera_rotation)

	camera_position = add_vectors(camera_position, direction)



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
	glLoadIdentity()

	# camera / all object transformations
	# reversed, since it's moving the world and not the camera
	glRotate(-camera_rotation[0], 1, 0, 0)
	glRotate(-camera_rotation[1], 0, 1, 0)
	glRotate(-camera_rotation[2], 0, 0, 1)

	glTranslate(-camera_position[0], -camera_position[1], -camera_position[2])

	# draw objects passed to the render_objects array
	for robj in render_objects:
		glUseProgram(robj[1])

		glBindVertexArray(robj[0])
		glDrawArrays(GL_TRIANGLES, 0, 3)

		glUseProgram(0)

	# draw a teapot
	glPushMatrix()
	glTranslatef(0, 0.8, 0)
	glColor3f(0, 1, 0)
	glutWireTeapot(1)
	glPopMatrix()

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

	glutSwapBuffers()


def idle_func():
	global pressed_keys, pressed_mouse, camera_rotation

	# get time
	current_time = glutGet(GLUT_ELAPSED_TIME)

	# camera translation
	if move_forward in pressed_keys:
		move_camera([0, 0, -1], current_time - pressed_keys[move_forward])
		pressed_keys[move_forward] = current_time

	if move_backward in pressed_keys:
		move_camera([0, 0, 1], current_time - pressed_keys[move_backward])
		pressed_keys[move_backward] = current_time

	if move_left in pressed_keys:
		move_camera([-1, 0, 0], current_time - pressed_keys[move_left])
		pressed_keys[move_left] = current_time

	if move_right in pressed_keys:
		move_camera([1, 0, 0], current_time - pressed_keys[move_right])
		pressed_keys[move_right] = current_time

	if move_up in pressed_keys:
		move_camera([0, 1, 0], current_time - pressed_keys[move_up])
		pressed_keys[move_up] = current_time

	if move_down in pressed_keys:
		move_camera([0, -1, 0], current_time - pressed_keys[move_down])
		pressed_keys[move_down] = current_time

	# camera rotation - TODO: way of selecting keypress/other mouse button in settings?
	if GLUT_RIGHT_BUTTON in pressed_mouse:
		degrees_x = field_of_view_h * pressed_mouse[GLUT_RIGHT_BUTTON][2] / window_width
		degrees_y = field_of_view_v * pressed_mouse[GLUT_RIGHT_BUTTON][3] / window_height

		camera_rotation[0] = camera_rotation[0] - sensitivity * degrees_y
		camera_rotation[1] = camera_rotation[1] - sensitivity * degrees_x

		pressed_mouse[GLUT_RIGHT_BUTTON][2] = 0
		pressed_mouse[GLUT_RIGHT_BUTTON][3] = 0

	# tell glut to re-run the display function
	glutPostRedisplay()



# set up glut window
glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(window_width, window_height)
glutInitWindowPosition(window_x, window_y)

window = glutCreateWindow(window_title)


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
#glDepthFunc(GL_LESS)  # default
#glShadeModel(GL_SMOOTH)  # default
#glShadeModel(GL_FLAT)

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(field_of_view_v, float(window_width)/float(window_height), clip_dist_near, clip_dist_far)

glMatrixMode(GL_MODELVIEW)  # TODO: move this to the display function?

