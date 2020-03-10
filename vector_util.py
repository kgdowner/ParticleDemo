from math import *

def add_vectors(vector1, vector2):
	return [vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2]]


def mult_vector(scalar, vector):
	return [scalar * vector[0], scalar * vector[1], scalar * vector[2]]


def normalize(vector):
	magnitude = vector[0]*vector[0] + vector[1]*vector[1] + vector[2]*vector[2]
	magnitude = sqrt(magnitude)

	out = [0, 0, 0]

	if vector[0] != 0:
		out[0] = vector[0] / magnitude

	if vector[1] != 0:
		out[1] = vector[1] / magnitude

	if vector[2] != 0:
		out[2] = vector[2] / magnitude

	return out


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


# euler-rodrigues formula
def rodrigues_mat3(axis, angle):
	# convert to radians & normalize axis
	angle = radians(angle)
	axis = normalize(axis)

	# pre-calculate some of the matrix's operations
	a = cos(angle/2)
	b = - axis[0] * sin(angle/2)
	c = - axis[1] * sin(angle/2)
	d = - axis[2] * sin(angle/2)
	aa, bb, cc, dd = a*a, b*b, c*c, d*d
	bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d

	# return the rotation matrix from rhodriguez's formula
	return [
		[aa+bb-cc-dd,   2*(bc+ad),   2*(bd-ac)],
		[  2*(bc-ad), aa+cc-bb-dd,   2*(cd+ab)],
		[  2*(bd+ac),   2*(cd-ab), aa+dd-bb-cc],
	]


def rot_vec_axis_angle(vector, axis, angle):
	rotation_matrix = rodrigues_mat3(axis, angle)
	return mult_mat3_vec3(rotation_matrix, vector)


def mult_mat3_vec3(m, v):
	return [
		m[0][0]*v[0] + m[0][1]*v[1] + m[0][2]*v[2],
		m[1][0]*v[0] + m[1][1]*v[1] + m[1][2]*v[2],
		m[2][0]*v[0] + m[2][1]*v[1] + m[2][2]*v[2],
	]


def mult_scalar_mat4(s, m):
	return [
		[s*m[0][0], s*m[0][1], s*m[0][2], s*m[0][3]],
		[s*m[1][0], s*m[1][1], s*m[1][2], s*m[1][3]],
		[s*m[2][0], s*m[2][1], s*m[2][2], s*m[2][3]],
		[s*m[3][0], s*m[3][1], s*m[3][2], s*m[3][3]],
	]


def mult_mat4_vec4(m, v):
	return [
		[m[0][0]*v[0] + m[0][1]*v[1] + m[0][2]*v[2] + m[0][3]*v[3]],
		[m[1][0]*v[0] + m[1][1]*v[1] + m[1][2]*v[2] + m[1][3]*v[3]],
		[m[2][0]*v[0] + m[2][1]*v[1] + m[2][2]*v[2] + m[2][3]*v[3]],
		[m[3][0]*v[0] + m[3][1]*v[1] + m[3][2]*v[2] + m[3][3]*v[3]],
	]


def mult_mat4(m1, m2):
	return [
		[
			m1[0][0]*m2[0][0] + m1[0][1]*m2[1][0] + m1[0][2]*m2[2][0] + m1[0][3]*m2[3][0],
			m1[0][0]*m2[0][1] + m1[0][1]*m2[1][1] + m1[0][2]*m2[2][1] + m1[0][3]*m2[3][1],
			m1[0][0]*m2[0][2] + m1[0][1]*m2[1][2] + m1[0][2]*m2[2][2] + m1[0][3]*m2[3][2],
			m1[0][0]*m2[0][3] + m1[0][1]*m2[1][3] + m1[0][2]*m2[2][3] + m1[0][3]*m2[3][3],
		],
		[
			m1[1][0]*m2[0][0] + m1[1][1]*m2[1][0] + m1[1][2]*m2[2][0] + m1[1][3]*m2[3][0],
			m1[1][0]*m2[0][1] + m1[1][1]*m2[1][1] + m1[1][2]*m2[2][1] + m1[1][3]*m2[3][1],
			m1[1][0]*m2[0][2] + m1[1][1]*m2[1][2] + m1[1][2]*m2[2][2] + m1[1][3]*m2[3][2],
			m1[1][0]*m2[0][3] + m1[1][1]*m2[1][3] + m1[1][2]*m2[2][3] + m1[1][3]*m2[3][3],
		],
		[
			m1[2][0]*m2[0][0] + m1[2][1]*m2[1][0] + m1[2][2]*m2[2][0] + m1[2][3]*m2[3][0],
			m1[2][0]*m2[0][1] + m1[2][1]*m2[1][1] + m1[2][2]*m2[2][1] + m1[2][3]*m2[3][1],
			m1[2][0]*m2[0][2] + m1[2][1]*m2[1][2] + m1[2][2]*m2[2][2] + m1[2][3]*m2[3][2],
			m1[2][0]*m2[0][3] + m1[2][1]*m2[1][3] + m1[2][2]*m2[2][3] + m1[2][3]*m2[3][3],
		],
		[
			m1[3][0]*m2[0][0] + m1[3][1]*m2[1][0] + m1[3][2]*m2[2][0] + m1[3][3]*m2[3][0],
			m1[3][0]*m2[0][1] + m1[3][1]*m2[1][1] + m1[3][2]*m2[2][1] + m1[3][3]*m2[3][1],
			m1[3][0]*m2[0][2] + m1[3][1]*m2[1][2] + m1[3][2]*m2[2][2] + m1[3][3]*m2[3][2],
			m1[3][0]*m2[0][3] + m1[3][1]*m2[1][3] + m1[3][2]*m2[2][3] + m1[3][3]*m2[3][3],
		],
	]


def rotation_mat4(angles):
	x = radians(angles[0])
	y = radians(angles[1])
	z = radians(angles[2])

	a = cos(x)
	b = sin(x)
	c = cos(y)
	d = sin(y)
	e = cos(z)
	f = cos(z)

	ad = a * d
	bd = b * d

	return [
		[          c * e,           -c * f,       d,  0],
		[ bd * e + a * f,  -bd * f + a * e,  -b * c,  0],
		[-ad * e + b * f,   ad * f + b * e,   a * c,  0],
		[              0,                0,       0,  1],
	]


def rot_mat4_x(angle):
	return [
		[1,          0,           0, 0],
		[0, cos(angle), -sin(angle), 0],
		[0, sin(angle),  cos(angle), 0],
		[0,          0,           0, 1]
	]


def rot_mat4_y(angle):
	return [
		[ cos(angle), 0, sin(angle), 0],
		[          0, 1,          0, 0],
		[-sin(angle), 0, cos(angle), 0],
		[          0, 0,          0, 1]
	]


def rot_mat4_z(angle):
	return [
		[cos(angle), -sin(angle), 0, 0],
		[sin(angle),  cos(angle), 0, 0],
		[         0,           0, 1, 0],
		[         0,           0, 0, 1]
	]


def rot_mat4_3(angles):
	x = rot_mat4_x(radians(angles[0]))
	y = rot_mat4_y(radians(angles[1]))
	z = rot_mat4_z(radians(angles[2]))

	#x = mult_scalar_mat4(-1, x)
	#y = mult_scalar_mat4(-1, y)
	#z = mult_scalar_mat4(-1, z)

	temp = mult_mat4(x, y)
	return mult_mat4(temp, z)