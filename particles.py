import render
import random

random.seed()

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
#test_vao = render.create_vao([0, 0, 0, 1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 1, 0, 0, 0, 1])
test_program = render.create_program(test_vert, test_frag, ["in_position, in_color"])

#square_vao = render.create_vao([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
square_vao = render.create_vao([
		-0.5, -0.5, 0,
		 0.5, -0.5, 0,
		-0.5,  0.5, 0,
		-0.5,  0.5, 0,
		 0.5, -0.5, 0,
		 0.5,  0.5, 0
	], [
		1, 1, 1,
		1, 1, 1,
		1, 1, 1,
		1, 1, 1,
		1, 1, 1,
		1, 1, 1
])


systems = []
particles = []

free_systems = []
free_particles = []

default_system_params = {
	"active": True,
	"particle_count": 1,
	"spawn_type": "instant",  # "instant" "continuous"
	"lifetime_min": 1,
	"lifetime_max": 1,
	"start_velocity_min": [0, 0, 0],
	"start_velocity_max": [0, 0, 0],
	"start_position": [0, 0, 0],  # todo more complex starting arrangement options
	"start_scale": 1,
	"end_scale": 1,
	"gravity": [0, 0, 0],
}


def create_particle_system(vao, shader, params=default_system_params):
	# get a free system or create a new one
	system_index = -1
	if len(free_systems) > 0:
		system_index = free_systems.pop()
	else:
		system_index = len(systems)
		systems.append({})

	# apply the system properties
	systems[system_index].clear()
	systems[system_index]["active"]				= params["active"]
	systems[system_index]["particle_count"]		= params["particle_count"]
	systems[system_index]["spawn_type"]			= params["spawn_type"]
	systems[system_index]["lifetime_min"]		= params["lifetime_min"]
	systems[system_index]["lifetime_max"]		= params["lifetime_max"]
	systems[system_index]["start_velocity_min"]	= params["start_velocity_min"]
	systems[system_index]["start_velocity_max"]	= params["start_velocity_max"]
	systems[system_index]["start_position"]		= params["start_position"]
	systems[system_index]["start_scale"]		= params["start_scale"]
	systems[system_index]["end_scale"]			= params["end_scale"]
	systems[system_index]["gravity"]			= params["gravity"]

	# create particles for this system
	for i in range(systems[system_index]["particle_count"]):
		create_particle(
			system_index,
			lifetime	= random.uniform(systems[system_index]["lifetime_min"], systems[system_index]["lifetime_max"]),
			scale		= systems[system_index]["start_scale"],
			position	= systems[system_index]["start_position"],
			velocity	= [
				random.uniform(systems[system_index]["start_velocity_min"][0], systems[system_index]["start_velocity_max"][0]),
				random.uniform(systems[system_index]["start_velocity_min"][1], systems[system_index]["start_velocity_max"][1]),
				random.uniform(systems[system_index]["start_velocity_min"][2], systems[system_index]["start_velocity_max"][2]),
			],
		)

	return system_index


def initialize_particle_system(system_index):
	# expensive!  TODO: add index list of particles to particle system?
	for particle_index in range(len(particles)):
		if particles[particle_index][0] == system_index:
			particles[particle_index][1]	= random.uniform(systems[system_index]["lifetime_min"], systems[system_index]["lifetime_max"]),
			particles[particle_index][2]	= systems[system_index]["start_scale"],
			particles[particle_index][3]	= systems[system_index]["start_position"],
			particles[particle_index][4]	= [
				random.uniform(systems[system_index]["start_velocity_min"], systems[system_index]["start_velocity_max"]),
				random.uniform(systems[system_index]["start_velocity_min"], systems[system_index]["start_velocity_max"]),
				random.uniform(systems[system_index]["start_velocity_min"], systems[system_index]["start_velocity_max"]),
			]


def free_particle_system(system_index):
	# clear particles
	for particle_index in range(len(particles)):
		if particles[particle_index][0] == system_index:
			free_particle(particle_index)

	# free system
	systems[system_index]["active"] = False
	free_systems.append(system_index)


def create_particle(system_index=-1, lifetime=1.0, scale=1.0, position=[0, 0, 0], velocity=[0, 0, 0]):
	# get a free particle or create a new one
	particle_index = -1
	if len(free_particles) > 0:
		particle_index = free_particles.pop()
	else:
		particle_index = len(particles)
		particles.append([0, 0, 0, 0, 0])

		# TEMP: for now just create render objects for every created particle
		render.render_objects.append({"vao":square_vao, "program":test_program, "matrix":[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]})

	# set initial properties
	particles[particle_index][0] = system_index
	particles[particle_index][1] = lifetime
	particles[particle_index][2] = scale
	particles[particle_index][3] = [position[0], position[1], position[2]]
	particles[particle_index][4] = [velocity[0], velocity[1], velocity[2]]

	return particle_index


def update_particle(particle_index, time_delta):
	system_index = particles[particle_index][0]

	if systems[system_index]["active"] and particles[particle_index][1] > 0:
		# update scale
		scale_delta = abs(systems[system_index]["start_scale"] - systems[system_index]["end_scale"])
		if scale_delta != 0:
			norm_scale = (particles[particle_index][2] - systems[system_index]["end_scale"]) / scale_delta
			new_scale = (particles[particle_index][1] - time_delta) * (norm_scale / particles[particle_index][1])
			particles[particle_index][2] = new_scale * scale_delta + systems[system_index]["end_scale"]
		#particles[particle_index][2] = (particles[particle_index][1] - time_delta) * (particles[particle_index][2] / particles[particle_index][1])


		# update position
		particles[particle_index][3][0] += particles[particle_index][4][0] * time_delta
		particles[particle_index][3][1] += particles[particle_index][4][1] * time_delta
		particles[particle_index][3][2] += particles[particle_index][4][2] * time_delta

		# update velocity
		particles[particle_index][4][0] += systems[system_index]["gravity"][0] * time_delta
		particles[particle_index][4][1] += systems[system_index]["gravity"][1] * time_delta
		particles[particle_index][4][2] += systems[system_index]["gravity"][2] * time_delta

		# update lifetime
		particles[particle_index][1] = particles[particle_index][1] - time_delta

		# some cleanup when the particle is done
		if particles[particle_index][1] <= 0:
			particles[particle_index][1] = 0
			particles[particle_index][2] = 0


def free_particle(particle_index):
	particles[particle_index][0] = -1
	free_particles.append(particle_index)


# update particle behavior inside the glut idle function (for now - TODO: threading?)
last_ic_time = 0
def ic(timestamp):
	global last_ic_time

	# time since the last function call (seconds)
	time_delta = (timestamp - last_ic_time) / 1000

	# update all the particles
	for particle_index in range(len(particles)):
		update_particle(particle_index, time_delta)

		# update all the render objects while we're here
		system_index = particles[particle_index][0]
		if system_index > -1 and systems[system_index]["active"]:
			render.render_objects[particle_index]["matrix"][0][0] = particles[particle_index][2]
			render.render_objects[particle_index]["matrix"][1][1] = particles[particle_index][2]
			render.render_objects[particle_index]["matrix"][2][2] = particles[particle_index][2]
			render.render_objects[particle_index]["matrix"][3][0] = particles[particle_index][3][0]
			render.render_objects[particle_index]["matrix"][3][1] = particles[particle_index][3][1]
			render.render_objects[particle_index]["matrix"][3][2] = particles[particle_index][3][2]
		else:
			render.render_objects[particle_index]["matrix"][0][0] = 0
			render.render_objects[particle_index]["matrix"][1][2] = 0
			render.render_objects[particle_index]["matrix"][2][2] = 0

	# record the time this was run for the movement deltas
	last_ic_time = timestamp

	# even the callbacks have callbacks? for main logic i guess TEMP
	if main_callback:
		main_callback(timestamp, time_delta)


# run the glut loops
render.idle_callback = ic
#render.render_loop()

def particle_loop():
	render.render_loop()