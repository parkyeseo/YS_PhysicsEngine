import pygame
from Matrix_Transform import *
from OpenGL.GL import *
import numpy as np


class Cube:
    def __init__(self, center=[0, 0, 0], size=1):
        """
        :param center: (x, y, z) for cube's center.
        :param size: Length of the cube's edge.
        """
        x, y, z = center
        half_size = size / 2

        # Cube vertices (homogeneous coordinates with w = 1)
        self.vertices_affine = np.array([
            [x - half_size, y - half_size, z - half_size, 1],
            [x - half_size, y + half_size, z - half_size, 1],
            [x + half_size, y + half_size, z - half_size, 1],
            [x + half_size, y - half_size, z - half_size, 1],
            [x - half_size, y - half_size, z + half_size, 1],
            [x - half_size, y + half_size, z + half_size, 1],
            [x + half_size, y + half_size, z + half_size, 1],
            [x + half_size, y - half_size, z + half_size, 1]
        ])

        # Cube vertices (for collision calculation)
        self.vertices = np.array([
            [x - half_size, y - half_size, z - half_size],
            [x - half_size, y + half_size, z - half_size],
            [x + half_size, y + half_size, z - half_size],
            [x + half_size, y - half_size, z - half_size],
            [x - half_size, y - half_size, z + half_size],
            [x - half_size, y + half_size, z + half_size],
            [x + half_size, y + half_size, z + half_size],
            [x + half_size, y - half_size, z + half_size]
        ])

        # Cube faces (each face uses 4 vertices)
        self.faces = [
            [0, 1, 2, 3],  # Bottom
            [4, 5, 6, 7],  # Top
            [0, 1, 5, 4],  # Left
            [2, 3, 7, 6],  # Right
            [1, 2, 6, 5],  # Front
            [0, 3, 7, 4]   # Back
        ]

        # Face colors (one color per face)
        self.colors = [
            [1, 0, 0],  # Red
            [0, 1, 0],  # Green
            [0, 0, 1],  # Blue
            [1, 1, 0],  # Yellow
            [1, 0, 1],  # Magenta
            [0, 1, 1]   # Cyan
        ]

        self.axes = np.array(np.eye(3))

    def draw(self):
        """Render the cube using OpenGL."""
        for i, face in enumerate(self.faces):
            glBegin(GL_QUADS)
            glColor3fv(self.colors[i])
            for vertex_index in face:
                glVertex3fv(self.vertices_affine[vertex_index][:-1])  # Ignore w component
            glEnd()

    def vertices_affine_to_vertices(self):
        """Dimensionality Reduction of vertices_affine(4D) to vertices(3D)"""
        vertices = []
        for vertice_aff in self.vertices_affine:
            vertices.append([vertice_aff[0], vertice_aff[1], vertice_aff[2]])
        return np.array(vertices)
    
    def update_axes(self):
        # Calculate edges from vertex[0] (lower-back-left corner)
        edge_x = self.vertices[3] - self.vertices[0]  # Edge along x-axis
        edge_y = self.vertices[1] - self.vertices[0]  # Edge along y-axis
        edge_z = self.vertices[4] - self.vertices[0]  # Edge along z-axis

        # Normalize the edges to get unit axes
        self.axes = np.array([
            edge_x / np.linalg.norm(edge_x),  # x-axis
            edge_y / np.linalg.norm(edge_y),  # y-axis
            edge_z / np.linalg.norm(edge_z)  # z-axis
        ])
    

    # Matrix Transformation #####################################################################

    def translate(self, pos3D):
        self.vertices_affine = self.vertices_affine @ translate_xyz(pos3D)
        self.vertices = self.vertices_affine_to_vertices()
        self.update_axes()

    def scale_x(self, size):
        self.vertices_affine = self.vertices_affine @ scale_x(1-size)
        self.vertices = self.vertices_affine_to_vertices()
        self.update_axes()
    
    def scale_y(self, size):
        self.vertices_affine = self.vertices_affine @ scale_y(1-size)
        self.vertices = self.vertices_affine_to_vertices()
        self.update_axes()
    
    def scale_z(self, size):
        self.vertices_affine = self.vertices_affine @ scale_z(1-size)
        self.vertices = self.vertices_affine_to_vertices()
        self.update_axes()

    def rotate_x(self, angle):
        self.vertices_affine = self.vertices_affine @ rotate_x(angle)
        self.vertices = self.vertices_affine_to_vertices()
        self.update_axes()

    def rotate_y(self, angle):
        self.vertices_affine = self.vertices_affine @ rotate_y(angle)
        self.vertices = self.vertices_affine_to_vertices()
        self.update_axes()

    def rotate_z(self, angle):
        self.vertices_affine = self.vertices_affine @ rotate_z(angle)
        self.vertices = self.vertices_affine_to_vertices()
        self.update_axes()

    #############################################################################################


    # Collision Detection #######################################################################

    @staticmethod
    def overlap_on_axis(cube1, cube2, axis):
        """Check if projections on the given axis overlap."""
        if np.linalg.norm(axis) < 1e-6:  # Skip near-zero axes
            return True

        axis = axis / np.linalg.norm(axis)
        projection1 = Cube.project(cube1, axis)
        projection2 = Cube.project(cube2, axis)
        return not (projection1[1] < projection2[0] or projection2[1] < projection1[0])

    @staticmethod
    def project(cube, axis):
        """Project the cube onto the given axis and return [min, max] range."""
        vertices = cube.vertices
        projections = np.dot(vertices, axis)
        return [np.min(projections), np.max(projections)]

    def check_collision(self, cube):
        """Check collision using SAT."""
        axes = np.vstack((self.axes, cube.axes))  # 6 face normals
        cross_products = [np.cross(a, b) for a in self.axes for b in cube.axes]  # 9 cross axes
        axes = np.vstack((axes, cross_products))

        for axis in axes:
            if not Cube.overlap_on_axis(self, cube, axis):
                return False
        return True
    
    #############################################################################################


    # Transformation ############################################################################

    def Transformation(self):
        key = pygame.key.get_pressed()
        mousePress = pygame.mouse.get_pressed()

        # Translation Transformation(left click)
        if key[pygame.K_a] and mousePress == (1, 0, 0):
            self.translate((0.03, 0, 0))
        if key[pygame.K_d] and mousePress == (1, 0, 0):
            self.translate((-0.03, 0, 0))
        if key[pygame.K_w] and mousePress == (1, 0, 0):
            self.translate((0, 0.03, 0))
        if key[pygame.K_s] and mousePress == (1, 0, 0):
            self.translate((0, -0.03, 0))
        if key[pygame.K_q] and mousePress == (1, 0, 0):
            self.translate((0, 0, 0.03))
        if key[pygame.K_e] and mousePress == (1, 0, 0):
            self.translate((0, 0, -0.03))

        # Rotation Transformation(right click)
        if key[pygame.K_a] and mousePress == (0, 0, 1):
            self.rotate_y(-0.03)
        if key[pygame.K_d] and mousePress == (0, 0, 1):
            self.rotate_y(0.03)
        if key[pygame.K_w] and mousePress == (0, 0, 1):
            self.rotate_x(-0.03)
        if key[pygame.K_s] and mousePress == (0, 0, 1):
            self.rotate_x(0.03)
        if key[pygame.K_q] and mousePress == (0, 0, 1):
            self.rotate_z(0.03)
        if key[pygame.K_e] and mousePress == (0, 0, 1):
            self.rotate_z(-0.03)

        # Scale Transformation(wheel)
        if key[pygame.K_a] and mousePress[1]:
            self.scale_x(0.05)
        if key[pygame.K_d] and mousePress[1]:
            self.scale_x(-0.05)
        if key[pygame.K_w] and mousePress[1]:
            self.scale_y(-0.05)
        if key[pygame.K_s] and mousePress[1]:
            self.scale_y(0.05)
        if key[pygame.K_q] and mousePress[1]:
            self.scale_z(0.05)
        if key[pygame.K_e] and mousePress[1]:
            self.scale_z(-0.05)

        # Camera Movement(non click)
        if key[pygame.K_a] and mousePress == (0, 0, 0):
            self.translate((-0.1, 0, 0))
        if key[pygame.K_d] and mousePress == (0, 0, 0):
            self.translate((0.1, 0, 0))
        if key[pygame.K_w] and mousePress == (0, 0, 0):
            self.translate((0, -0.1, 0))
        if key[pygame.K_s] and mousePress == (0, 0, 0):
            self.translate((0, 0.1, 0))
        if key[pygame.K_q] and mousePress == (0, 0, 0):
            self.translate((0, 0, -0.1))
        if key[pygame.K_e] and mousePress == (0, 0, 0):
            self.translate((0, 0, 0.1))
        if key[pygame.K_UP] and mousePress == (0, 0, 0):
            self.rotate_x(0.01)
        if key[pygame.K_DOWN] and mousePress == (0, 0, 0):
            self.rotate_x(-0.01)
        if key[pygame.K_LEFT] and mousePress == (0, 0, 0):
            self.rotate_z(0.01)
        if key[pygame.K_RIGHT] and mousePress == (0, 0, 0):
            self.rotate_z(-0.01)

    #############################################################################################
