import numpy as np

# trying to write the function in a single line
kinetic_energy = lambda mass,vel: 0.5*mass*vel**2
potential_energy = lambda mass,gravity,height: mass*gravity*height
displacement = lambda vel,time,accn: vel*time+0.5*accn*time**2
final_vel = lambda vel,accn,time: vel+accn*time
avg_vel = lambda distance,time: distance/time
gravitational_force = lambda m1,m2,r: 6.6743e-11*m1*m2/r**2
wave_speed = lambda frequency,wave_length: frequency*wave_length
force = lambda mass,accn,angle: mass*accn*np.cos(np.degrees(angle))
