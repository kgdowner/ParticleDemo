# handles the window and the opengl rendering inside it

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
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
move_speed	= 1		# 1 unit/time? (TODO: implement / convert to seconds?)


# globals
camera_rotation	= [0, 0, 0]
camera_position	= [0, 0, 6]

movement_event		= False
movement_start_x	= 0
movement_start_y	= 0
degrees_x_last		= 0
degrees_y_last		= 0



# callbacks
def keyboard_func(key, x, y):
	global camera_position, camera_rotation

	if key == b'w':
		direction = rot3([0, 0, -1], camera_rotation)
		camera_position = add_vectors(camera_position, direction)

	if key == b'a':
		direction = rot3([-1, 0, 0], camera_rotation)
		camera_position = add_vectors(camera_position, direction)

		print("a")
	if key == b's':
		direction = rot3([0, 0, 1], camera_rotation)
		camera_position = add_vectors(camera_position, direction)

	if key == b'd':
		direction = rot3([1, 0, 0], camera_rotation)
		camera_position = add_vectors(camera_position, direction)

	if key == b' ':
		direction = rot3([0, 1, 0], camera_rotation)
		camera_position = add_vectors(camera_position, direction)


def special_func(key, x, y):
	global camera_position, camera_rotation

	if key == 114:  # ctrl
		direction = rot3([0, -1, 0], camera_rotation)
		camera_position = add_vectors(camera_position, direction)


def mouse_func(button, state, x, y):
	global movement_event, movement_start_x, movement_start_y
	global degrees_x_last, degrees_y_last

	# start/end camera movement when right click is pressed/released
	if button == 2:
		if state == 0:
			movement_event = True
			movement_start_x = x
			movement_start_y = y
		else:
			movement_event = False
			degrees_x_last = 0
			degrees_y_last = 0


def motion_func(x, y):
	global camera_position, camera_rotation
	global degrees_x_last, degrees_y_last
	#global sensitivity  # FIXME: remove? should be working without - already init'd not assigned here


	# rotate camera
	if movement_event:
		degrees_x = field_of_view_h * (x - movement_start_x) / window_width
		degrees_y = field_of_view_v * (y - movement_start_y) / window_height

		camera_rotation[0] = camera_rotation[0] + sensitivity * (degrees_y_last - degrees_y)
		camera_rotation[1] = camera_rotation[1] + sensitivity * (degrees_x_last - degrees_x)

		degrees_x_last = degrees_x	# TODO: calculate this based on last frame's mouse pos, not initial mouse pos of event
		degrees_y_last = degrees_y	# will remove need for degree_*_last backtracing


def display_func():
	global camera_rotation, camera_position

	# clear screen and reset transform matrix
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()


	# camera / all object transformations
	# reversed, since it's moving the world and not the camera
	glRotate(-camera_rotation[0], 1, 0, 0)
	glRotate(-camera_rotation[1], 0, 1, 0)
	glRotate(-camera_rotation[2], 0, 0, 1)

	glTranslate(-camera_position[0], -camera_position[1], -camera_position[2])


	# draw a teapot
	glPushMatrix()
	glTranslatef(0, 0.8, 0)
	glColor3f(0, 1, 0)
	#glutSolidCube(1)
	#glutSolidTeapot(1)
	glutWireTeapot(1)
	glPopMatrix()


	# 3D Coordinates Indicator
	glBegin(GL_LINES)

	#glColor3f(1.0, 0.0, 0.0)
	#glVertex3f( 2.0, 0.0, 0.0)
	#glVertex3f(-2.0, 0.0, 0.0)

	glColor3f(0.0, 1.0, 0.0)
	glVertex3f(0.0,  2.0, 0.0)
	glVertex3f(0.0, -2.0, 0.0)

	#glColor3f(0.0, 0.0, 1.0)
	#glVertex3f(0.0, 0.0,  2.0)
	#glVertex3f(0.0, 0.0, -2.0)

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
	# program logic here

	# TODO: move all the camera movement updates here from the keyboard/mouse funcs

	# tell glut to re-run the display function
	glutPostRedisplay()



# set up glut window
glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(window_width, window_height)
glutInitWindowPosition(window_x, window_y)

window = glutCreateWindow(window_title)


# register glut callbacks
glutKeyboardFunc(keyboard_func)
glutSpecialFunc(special_func)
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


# start render loop  - TODO: move this to the main application
#glutMainLoop()