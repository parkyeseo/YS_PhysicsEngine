import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import random

class Sphere:
    def __init__(self, center, radius, color, velocity):
        """
        :param center: Sphere's center (x, y, z).
        :param radius: Radius of the sphere.
        :param color: Sphere's color in RGB (e.g., [1, 0, 0] for red).
        :param velocity: Sphere's velocity (dx, dy, dz).
        """
        self.center = np.array(center, dtype=float)
        self.radius = radius
        self.color = color
        self.original_color = color
        self.velocity = np.array(velocity, dtype=float)

    def draw(self):
        """Render the sphere."""
        num_slices = 36
        num_stacks = 18
        glPushMatrix()
        glTranslatef(*self.center)
        glColor3f(*self.color)
        for i in range(num_stacks):
            theta1 = i * np.pi / num_stacks
            theta2 = (i + 1) * np.pi / num_stacks
            glBegin(GL_TRIANGLE_STRIP)
            for j in range(num_slices + 1):
                phi = j * 2 * np.pi / num_slices
                for theta in (theta1, theta2):
                    x = self.radius * np.sin(theta) * np.cos(phi)
                    y = self.radius * np.sin(theta) * np.sin(phi)
                    z = self.radius * np.cos(theta)
                    glVertex3f(x, y, z)
            glEnd()
        glPopMatrix()

    def move(self):
        """Update the sphere's position based on its velocity."""
        self.center += self.velocity

    def check_collision(self, other_sphere):
        """Check if this sphere collides with another sphere."""
        distance = np.linalg.norm(self.center - other_sphere.center)
        return distance <= (self.radius + other_sphere.radius)

    def handle_wall_collision(self, bounds):
        """Bounce off walls if the sphere hits the screen bounds."""
        for i in range(3):  # x, y, z axes
            if self.center[i] - self.radius < bounds[i][0] or self.center[i] + self.radius > bounds[i][1]:
                self.velocity[i] *= -1  # Reverse direction
                self.center[i] = np.clip(self.center[i], bounds[i][0] + self.radius, bounds[i][1] - self.radius)

    def set_color(self, color):
        """Set the color of the sphere."""
        self.color = color

    def reset_color(self):
        """Reset the sphere's color to its original state."""
        self.color = self.original_color


pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("YS3D Sphere Collision")
glEnable(GL_DEPTH_TEST)


glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, (800 / 600), 0.1, 100)
glMatrixMode(GL_MODELVIEW)


num_spheres = 20
spheres = []
bounds = [(-10, 10), (-10, 10), (-20, -5)]  # x, y, z bounds for walls

# create random sphere
for _ in range(num_spheres):
    center = [random.uniform(bounds[0][0] + 1, bounds[0][1] - 1),
                random.uniform(bounds[1][0] + 1, bounds[1][1] - 1),
                random.uniform(bounds[2][0] + 1, bounds[2][1] - 1)]
    radius = random.uniform(0.5, 1.5)
    color = [random.random(), random.random(), random.random()]
    velocity = [random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)]
    spheres.append(Sphere(center=center, radius=radius, color=color, velocity=velocity))

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Refresh
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()


    # Sphere Collision and Movement
    for i, sphere in enumerate(spheres):
        sphere.move()
        sphere.handle_wall_collision(bounds)

        # Sphere Collision Detection
        collision_detected = False
        for j, other_sphere in enumerate(spheres):
            if i != j and sphere.check_collision(other_sphere):
                collision_detected = True
                # Reverse Speed
                sphere.velocity *= -1
                other_sphere.velocity *= -1

        # Collision -> Red
        if collision_detected:
            sphere.set_color([1, 0, 0])
        else:
            sphere.reset_color()

        sphere.draw()

    pygame.display.flip()
    clock.tick(60)

    

