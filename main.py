#!/usr/bin/env python

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *


# Global Values
window = 0
window_width = 1024
window_height = 768
window_x = 2300
window_y = 600

field_of_view = 45
clip_dist_near = 0.1
clip_dist_far = 100

camera_rotation = [0, 0, 0]
camera_position = [0, 0, 6]

sensitivity = 4  # 1 = direct translation from pixels to FOV angle moved
move_speed = 1  # 1 unit/time? (TODO: implement / convert to seconds?)



def InitGL(Width, Height):
	global field_of_view, clip_dist_near, clip_dist_far

	glClearColor(0.0, 0.0, 0.0, 0.0)
	glClearDepth(1.0)
	glEnable(GL_DEPTH_TEST)
	#glDepthFunc(GL_LESS)  # default
	#glShadeModel(GL_SMOOTH)  # default
	#glShadeModel(GL_FLAT)

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(field_of_view, float(Width)/float(Height), clip_dist_near, clip_dist_far)

	glMatrixMode(GL_MODELVIEW)


def DrawGLScene():
	global camera_rotation, camera_position

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	# clear all transform matrices
	glLoadIdentity()


	# camera / all object transformations
	# reversed, since it's really moving the objects and not the camera
	glRotate(-camera_rotation[0], 1, 0, 0)
	glRotate(-camera_rotation[1], 0, 1, 0)
	glRotate(-camera_rotation[2], 0, 0, 1)

	glTranslate(-camera_position[0], -camera_position[1], -camera_position[2])

	#gluLookAt(0, 6, 0, 0, 0, 0, 0, 0, -1)  # another method, but handling up vecors is tricky


	# Draw a teapot
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


def add_vectors(vector1, vector2):
	return [vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2]]


def unit_vector(vector):
	magnitude = vector[0]*vector[0] + vector[1]*vector[1] + vector[2]*vector[2]
	magnitude = sqrt(magnitude)

	return [vector[0]/magnitude, vector[1]/magnitude, vector[2]/magnitude]


def rotx(vector, angle):
	angle = radians(angle)

	m = [[1, 0, 0], [0, cos(angle), -sin(angle)], [0, sin(angle), cos(angle)]]

	x = m[0][0]*vector[0] + m[0][1]*vector[1] + m[0][2]*vector[2]
	y = m[1][0]*vector[0] + m[1][1]*vector[1] + m[1][2]*vector[2]
	z = m[2][0]*vector[0] + m[2][1]*vector[1] + m[2][2]*vector[2]

	return [x, y, z]


def roty(vector, angle):
	angle = radians(angle)

	m = [[cos(angle), 0, sin(angle)], [0, 1, 0], [-sin(angle), 0, cos(angle)]]

	x = m[0][0]*vector[0] + m[0][1]*vector[1] + m[0][2]*vector[2]
	y = m[1][0]*vector[0] + m[1][1]*vector[1] + m[1][2]*vector[2]
	z = m[2][0]*vector[0] + m[2][1]*vector[1] + m[2][2]*vector[2]

	return [x, y, z]


def rotz(vector, angle):
	angle = radians(angle)

	m = [[cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]

	x = m[0][0]*vector[0] + m[0][1]*vector[1] + m[0][2]*vector[2]
	y = m[1][0]*vector[0] + m[1][1]*vector[1] + m[1][2]*vector[2]
	z = m[2][0]*vector[0] + m[2][1]*vector[1] + m[2][2]*vector[2]

	return [x, y, z]


def rot3(vector, angles):
	vector = rotx(vector, angles[0])
	vector = roty(vector, angles[1])
	vector = rotz(vector, angles[2])

	return vector


def keyboard_func(key, x, y):
	global camera_position, camera_rotation

	print("key:", key, x, y)

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

	print("spec:", key, x, y)

	if key == 114:  # ctrl
		direction = rot3([0, -1, 0], camera_rotation)
		camera_position = add_vectors(camera_position, direction)


degrees_x_last, degrees_y_last = 0, 0
def motion_func(x, y):
	global camera_position, camera_rotation, motion_x_old, motion_y_old
	global degrees_x_last, degrees_y_last
	global sensitivity

	print("motion:", x, y)

	# rotate camera
	if movement_event:
		field_of_view_h = degrees(2 * atan(tan(field_of_view / 2) * window_width / window_height))

		degrees_x = field_of_view_h * (x - movement_start_x) / window_width
		degrees_y = field_of_view * (y - movement_start_y) / window_height

		# TODO: perhaps full 3-axis movement at some point?
		camera_rotation[0] = camera_rotation[0] + sensitivity * (degrees_y_last - degrees_y)
		camera_rotation[1] = camera_rotation[1] + sensitivity * (degrees_x_last - degrees_x)

		degrees_x_last = degrees_x
		degrees_y_last = degrees_y


movement_event, movement_start_x, movement_start_y = False, 0, 0
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


def main():
	global window, window_width, window_height, window_x, window_y

	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
	glutInitWindowSize(window_width, window_height)
	glutInitWindowPosition(window_x, window_y)

	window = glutCreateWindow('OpenGL Python Cube')

	glutDisplayFunc(DrawGLScene)
	glutIdleFunc(DrawGLScene)

	glutKeyboardFunc(keyboard_func)
	glutSpecialFunc(special_func)
	glutMotionFunc(motion_func)
	glutMouseFunc(mouse_func)

	InitGL(window_width, window_height)
	glutMainLoop()



if __name__ == "__main__":
	main() 





























# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *

# window = 0
# width, height = 500, 400

# def draw_rect(x, y, width, height):
# 	glBegin(GL_QUADS)
# 	glVertex2f(x, y)
# 	glVertex2f(x+width, y)
# 	glVertex2f(x+width, y+height)
# 	glVertex2f(x, y+height)
# 	glEnd()

# def draw():
# 	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
# 	glLoadIdentity()
# 	refresh2d(width, height)

# 	# draw something ...
# 	glColor3f(0, 1, 0)
# 	draw_rect(10, 10, 200, 100)

# 	glutSwapBuffers()

# def refresh2d(width, height):
# 	glViewport(0, 0, width, height)

# 	glMatrixMode(GL_PROJECTION)
# 	glLoadIdentity()
# 	glOrtho(0.0, width, 0.0, height, 0.0, 1.0)

# 	glMatrixMode(GL_MODELVIEW)
# 	glLoadIdentity()


# # init gl
# glutInit()
# glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
# glutInitWindowSize(width, height)
# #glutInitWindowPosition(0, 0)
# window = glutCreateWindow("noobs")
# glutDisplayFunc(draw)
# glutIdleFunc(draw)
# glutMainLoop()