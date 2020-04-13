#!/usr/bin/env python

import particles
import random

system_create_times = []

def mc(timestamp, delta):
	global system_create_times

	if random.random() < 0.01:
		system_index = particles.create_particle_system(particles.square_vao, particles.test_program, {
			"active": True,
			"particle_count": 100,
			"spawn_type": "instant",  # "instant" "continuous"  ?
			"lifetime_min": 0,
			"lifetime_max": 4,
			"start_velocity_min": [-10, -10, -10],
			"start_velocity_max": [10, 10, 10],
			"start_position": [random.uniform(-10, 10), random.uniform(4, 12), random.uniform(-10, 10)],
			"start_scale": 1,
			"end_scale": 0,
			"gravity": [0, -10, 0],
		})
		system_create_times.append((system_index, timestamp))

	for ct in system_create_times:
		if (ct[1] + particles.systems[ct[0]]["lifetime_max"]*1000) < timestamp:
			particles.free_particle_system(ct[0])
			system_create_times.remove(ct)

	#print("System Count: ", len(particles.systems), "\t\tParticle Count: ", len(particles.particles), "\t\t", len(particles.free_systems))

particles.main_callback = mc


particles.particle_loop()