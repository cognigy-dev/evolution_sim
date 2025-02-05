import pygame
import random
import math
from perspective_example import Creature3D, Herbivore3D
from perspective_grid import PerspectiveGrid
from graphics.graphics.prototype.plant3d import Plant3D

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("3D Perspective Demo")

# Simplified Camera
class Camera:
    def __init__(self):
        self.zoom = 1.0
        self.x = 0
        self.y = 0
        self.min_zoom = 1.0
        self.max_zoom = 4.0
        
    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.zoom = min(self.max_zoom, self.zoom * 1.1)
                # Zoom towards mouse
                self.x = mouse_x - (mouse_x - self.x) * 1.1
                self.y = mouse_y - (mouse_y - self.y) * 1.1
            elif event.button == 5:  # Mouse wheel down
                self.zoom = max(self.min_zoom, self.zoom / 1.1)
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                dx, dy = event.rel
                self.x += dx
                self.y += dy

# Create camera
camera = Camera()

# Create perspective grid
grid = PerspectiveGrid(WINDOW_WIDTH, WINDOW_HEIGHT)

# Create initial plants
plants = []
for _ in range(10):
    x = random.randint(-600, 600)
    z = random.randint(0, 600)
    plants.append(Plant3D(x, 0, z))

# Create creatures with movement
creatures = [
    Creature3D(300, 400, 100),      # Left omnivore (closer)
    Creature3D(500, 350, 400),      # Right omnivore (further back)
    Herbivore3D(400, 350, 200),     # Center herbivore
]

# Pre-create the world surface
world_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        camera.handle_input(event)

    # Update plants with faster growth
    new_plants = []
    for plant in plants[:]:
        for _ in range(2):  # Update twice per frame for faster growth
            plant_child = plant.update()
            if plant_child:
                new_plants.append(plant_child)
    plants.extend(new_plants)
    
    if len(plants) > 200:
        plants = plants[:200]

    # Update creatures with movement
    for creature in creatures:
        creature.update()
        # Add wandering behavior
        creature.x += math.sin(creature.sway_time * 0.5) * 2
        creature.z += math.cos(creature.sway_time * 0.3) * 1

    # Draw
    world_surface.fill((200, 200, 200))
    grid.draw(world_surface)
    
    # Sort and draw all objects
    all_objects = [(p, p.z) for p in plants] + [(c, c.z) for c in creatures]
    for obj, _ in sorted(all_objects, key=lambda x: x[1], reverse=True):
        if isinstance(obj, Plant3D):
            obj.draw(world_surface, grid)
        else:
            obj.draw(world_surface)
    
    # Apply camera transform
    scaled_size = (int(WINDOW_WIDTH * camera.zoom), int(WINDOW_HEIGHT * camera.zoom))
    screen.fill((200, 200, 200))
    scaled = pygame.transform.scale(world_surface, scaled_size)
    screen.blit(scaled, (camera.x, camera.y))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit() 