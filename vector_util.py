from math import *

def add_vectors(vector1, vector2):
	return [vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2]]


def mult_vector(scalar, vector):
	return [scalar * vector[0], scalar * vector[1], scalar * vector[2]]


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