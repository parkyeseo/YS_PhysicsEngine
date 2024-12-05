import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Mesh3D import *


pygame.init()
display = (1600, 900)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("YS Physics Engine")

gluPerspective(60, (display[0] / display[1]), 0.1, 100.0)
glTranslatef(0.0, 0.0, -3.0)
glEnable(GL_DEPTH_TEST)

# Camera setup
gluLookAt(0, 0, 0, 0, 0.5, 0.5, 0, 1, 0)

# Define cubes
mesh0 = Cube(center=[0, 0, 0], size=1)
mesh1 = Cube(center=[2.0, 0, 0], size=1)
selected_mesh = 0

clock = pygame.time.Clock()


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    # Select Mesh (0: mesh0, 1: mesh1)
    if pygame.key.get_pressed()[pygame.K_0]:
        selected_mesh = 0
    if pygame.key.get_pressed()[pygame.K_1]:
        selected_mesh = 1

    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Draw Mesh 0
    mesh0.draw()

    # Draw Mesh 1
    mesh1.draw()

    # Transform Mesh
    if pygame.mouse.get_pressed() == (0, 0, 0):
        mesh0.Transformation()
        mesh1.Transformation()
    else:
        if selected_mesh == 0:
            mesh0.Transformation()
        if selected_mesh == 1:
            mesh1.Transformation()


    if mesh0.check_collision(mesh1):
        mesh0.colors = [
            [1, 0, 0],  # Red
            [1, 0, 0],  
            [1, 0, 0],  
            [1, 0, 0],  
            [1, 0, 0],  
            [1, 0, 0]   
        ]
        mesh1.colors = [
            [1, 0, 0],  # Red
            [1, 0, 0],  
            [1, 0, 0],  
            [1, 0, 0],  
            [1, 0, 0],  
            [1, 0, 0]   
        ]
        print("Collision!")
    else:
        mesh0.colors = [
            [1, 0, 0],  # Red
            [0, 1, 0],  # Green
            [0, 0, 1],  # Blue
            [1, 1, 0],  # Yellow
            [1, 0, 1],  # Magenta
            [0, 1, 1]   # Cyan
        ]
        mesh1.colors = [
            [1, 0, 0],  # Red
            [0, 1, 0],  # Green
            [0, 0, 1],  # Blue
            [1, 1, 0],  # Yellow
            [1, 0, 1],  # Magenta
            [0, 1, 1]   # Cyan
        ]

    pygame.display.flip()
    clock.tick(60)
