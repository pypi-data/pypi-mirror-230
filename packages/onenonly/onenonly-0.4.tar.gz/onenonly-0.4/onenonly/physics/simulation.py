from matplotlib import pyplot as plt
from scipy.integrate import odeint
import numpy as np

class InterferencePattern:
    def __init__(self,wavelength,distance,screen_distance,screen_width):
        self.wavelength = wavelength
        self.distance = distance
        self.screen_distance = screen_distance
        self.screen_width = screen_width

    def calculate_intensity(self,x):
        intensity = np.zeros_like(x)
        for source_x in [-self.distance/2,self.distance/2]:
            path_difference = np.sqrt((x - source_x)**2 + self.screen_distance**2)
            intensity += np.cos(2 * np.pi * path_difference/self.wavelength)
        return intensity

    def simulate(self):
        x = np.linspace(-self.screen_width/2,self.screen_width/2,1000)
        intensity = self.calculate_intensity(x)
        intensity /= np.max(intensity)
        plt.figure(figsize=(10,5))
        plt.grid(True)
        plt.plot(x,intensity,lw=2)
        plt.title("Interference Pattern")
        plt.xlabel("Position on Screen")
        plt.ylabel("Intensity")
        plt.show()


class FreeFall:
    def __init__(self, initial_height,total_time,g=9.81,time_stamp=0.01):
        self.initial_height = initial_height
        self.total_time = total_time
        self.time_stamp = time_stamp
        self.g = g

    def simulate(self):
        times = []
        heights = []
        time = 0.0
        height = self.initial_height

        while time <= self.total_time:
            times.append(time)
            heights.append(height)
            height = self.initial_height - 0.5 * self.g * time**2
            time += self.time_stamp

        plt.grid(True)
        plt.legend(title = f"gravity: {self.g}")
        plt.yscale("log")
        plt.plot(times, heights)
        plt.xlabel("Time (seconds)")
        plt.ylabel("Height (meters)")
        plt.title("Free Fall Simulation")
        plt.show()

        
class GravitationalLensing:
    def __init__(self,M,grid_size=500):
        self.M = M
        self.grid_size = grid_size
        self.G = 6.67430e-11
        self.c = 299792458.0

    def simulate(self):
        rs = (2 * self.G * self.M) / self.c**2
        x = np.linspace(-2 * rs, 2 * rs, self.grid_size)
        y = np.linspace(-2 * rs, 2 * rs, self.grid_size)
        x,y = np.meshgrid(x, y)
        phi = -self.G * self.M / np.sqrt(x**2 + y**2)

        plt.figure(figsize=(8,6))
        plt.contourf(x,y,phi,levels=100,cmap="coolwarm")
        plt.colorbar(label="Gravitational Potential")
        plt.title("Gravitational Lensing by a Black Hole")
        plt.xlabel("X-coordinate")
        plt.ylabel("Y-coordinate")
        plt.show()


class ProjectileMotion:
    def __init__(self,initial_velocity,launch_angle,g=9.81,initial_height=0.0,timestep=0.01):
        self.initial_velocity = initial_velocity
        self.launch_angle = launch_angle
        self.initial_height = initial_height
        self.timestep = timestep
        self.title = g
        self.g = g

    def simulate(self):
        initial_velocity_x = self.initial_velocity * np.cos(np.radians(self.launch_angle))
        initial_velocity_y = self.initial_velocity * np.sin(np.radians(self.launch_angle))
        total_time = (2 * initial_velocity_y) / self.g

        time_points = []
        x_points = []
        y_points = []

        time = 0.0
        x = 0.0
        y = self.initial_height

        while time <= total_time:
            time_points.append(time)
            x_points.append(x)
            y_points.append(y)
            x = initial_velocity_x * time
            y = self.initial_height + (initial_velocity_y * time) - (0.5 * self.g * time**2)
            time += self.timestep

        plt.grid(True)
        plt.legend(title = f"gravity: {self.g}")
        plt.figure(figsize=(8,6))
        plt.plot(x_points, y_points)
        plt.xlabel('Horizontal Distance (m)')
        plt.ylabel('Vertical Height (m)')
        plt.title('Projectile Motion Simulation')
        plt.show()


class SimplePendulumSimulation:
    def __init__(self,length=1.0,initial_angle=np.pi/4,g=9.81,initial_angular_velocity=0.0,total_time=10,num_points=1000):
        self.length = length
        self.initial_angle = initial_angle
        self.initial_angular_velocity = initial_angular_velocity
        self.total_time = total_time
        self.num_points = num_points
        self.g = g

    def pendulum_equation(self,theta,t):
        theta_dot = theta[1]
        theta_double_dot = -(self.g / self.length) * np.sin(theta[0])
        return [theta_dot,theta_double_dot]

    def simulate(self):
        t = np.linspace(0,self.total_time,self.num_points)
        initial_theta = [self.initial_angle,self.initial_angular_velocity]

        theta_solution = odeint(self.pendulum_equation,initial_theta,t)
        angles = theta_solution[:,0]

        plt.grid(True)
        plt.legend(title = f"gravity: {self.g}")
        plt.figure(figsize=(8,6))
        plt.plot(t,angles)
        plt.title("Simple Pendulum Motion")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Angle (radians)")
        plt.show()

"""
cmap: 
    coolwarm
    nipy_spectral
    viridis
    plasma
    inferno
    magma
    winter
    summer
    spring
    prism
    pink
    jet
    hsv
    hot
    gray
    flag
    copper
    cool
    bone
    autumn
"""
