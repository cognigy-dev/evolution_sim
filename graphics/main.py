import pygame
import random
from omnivore import Omnivore
from herbivore import Herbivore
from plant import Plant
from carnivore import Carnivore
from ground import Ground
from config import *

# Initialize Pygame
pygame.init()

# Grid dimensions
GRID_WIDTH = 60  # Number of squares wide
GRID_HEIGHT = 30  # Number of squares high
SQUARE_SIZE = 30  # Pixels per square

# Calculate window size based on grid
WINDOW_WIDTH = GRID_WIDTH * SQUARE_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * SQUARE_SIZE

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Ecosystem Simulation")

# Colors
BACKGROUND = (173, 216, 230)  # Light blue sky
GRID_COLOR = (180, 180, 180)  # Grid lines
GROUND_COLOR_1 = (227, 213, 202)  # Lighter beige
GROUND_COLOR_2 = (215, 204, 195)  # Slightly darker beige

# Helper function to convert grid coordinates to screen coordinates
def grid_to_screen(grid_x, grid_y):
    return grid_x * SQUARE_SIZE, grid_y * SQUARE_SIZE

# Create initial plants
plants = []
for _ in range(10):
    grid_x = random.randint(0, GRID_WIDTH - 1)
    grid_y = random.randint(0, GRID_HEIGHT - 1)
    x, y = grid_to_screen(grid_x, grid_y)
    plants.append(Plant(x, y))

# Create game objects - place them in specific grid squares
# Place omnivores
omnivore1_grid_x = GRID_WIDTH // 2
omnivore1_grid_y = GRID_HEIGHT // 2
x, y = grid_to_screen(omnivore1_grid_x, omnivore1_grid_y)
omnivore1 = Omnivore(x, y)

# Second omnivore in opposite corner
omnivore2_grid_x = GRID_WIDTH * 3 // 4  # Place at 3/4 of grid width
omnivore2_grid_y = GRID_HEIGHT // 3
x, y = grid_to_screen(omnivore2_grid_x, omnivore2_grid_y)
omnivore2 = Omnivore(x, y)

# Add herbivores at random grid positions
herbivores = []
for _ in range(3):  # Start with 3 herbivores
    grid_x = random.randint(0, GRID_WIDTH - 1)
    grid_y = random.randint(0, GRID_HEIGHT - 1)
    x, y = grid_to_screen(grid_x, grid_y)
    print(f"Creating herbivore at ({x}, {y})")
    herbivores.append(Herbivore(x, y))

# Add carnivores at specific positions
carnivore1_grid_x = GRID_WIDTH // 4  # Place at 1/4 of grid width
carnivore1_grid_y = GRID_HEIGHT // 2
x, y = grid_to_screen(carnivore1_grid_x, carnivore1_grid_y)
carnivore1 = Carnivore(x, y)

# Second carnivore
carnivore2_grid_x = GRID_WIDTH * 3 // 4  # Place at 3/4 of grid width
carnivore2_grid_y = GRID_HEIGHT * 2 // 3  # Place at 2/3 of grid height
x, y = grid_to_screen(carnivore2_grid_x, carnivore2_grid_y)
carnivore2 = Carnivore(x, y)

# Add after pygame.init()
class Camera:
    def __init__(self, window_width, window_height, grid_width, grid_height):
        self.window_width = window_width
        self.window_height = window_height
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.zoom = 1.0
        self.x = 0
        self.y = 0
        self.min_zoom = max(window_width / (grid_width * SQUARE_SIZE),
                           window_height / (grid_height * SQUARE_SIZE))
        self.max_zoom = 3.0
        
    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up (zoom in)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                old_zoom = self.zoom
                self.zoom = min(self.max_zoom, self.zoom * 1.1)
                # Zoom towards mouse position
                if self.zoom != old_zoom:
                    self.x = mouse_x - (mouse_x - self.x) * (self.zoom/old_zoom)
                    self.y = mouse_y - (mouse_y - self.y) * (self.zoom/old_zoom)
                    
            elif event.button == 5:  # Mouse wheel down (zoom out)
                old_zoom = self.zoom
                self.zoom = max(self.min_zoom, self.zoom / 1.1)
                if self.zoom != old_zoom:
                    # Keep center when zooming out
                    center_x = self.window_width / 2
                    center_y = self.window_height / 2
                    self.x = center_x - (center_x - self.x) * (self.zoom/old_zoom)
                    self.y = center_y - (center_y - self.y) * (self.zoom/old_zoom)
                    
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                dx, dy = event.rel
                self.x += dx
                self.y += dy

    def apply(self, surface):
        # Calculate scaled size
        scaled_width = int(self.window_width * self.zoom)
        scaled_height = int(self.window_height * self.zoom)
        scaled = pygame.transform.scale(surface, (scaled_width, scaled_height))
        
        # Create a surface for the visible area
        visible = pygame.Surface((self.window_width, self.window_height))
        visible.fill(BACKGROUND)
        
        # Draw the scaled surface at the camera position
        visible.blit(scaled, (self.x, self.y))
        return visible

# Create camera after setting up the display
camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_WIDTH, GRID_HEIGHT)

# After creating the display
ground = Ground(GRID_WIDTH, GRID_HEIGHT, SQUARE_SIZE)

# Game loop
running = True
clock = pygame.time.Clock()

def draw_animals(grid):
    if GRAPHICS_AVAILABLE:
        # Draw with advanced graphics
        for x, y in grid.omnivores:
            if grid.grid[y][x]:
                screen_x = x * CELL_SIZE - (45 - CELL_SIZE) // 2  # Center 45px sprite on 30px grid
                screen_y = y * CELL_SIZE - (45 - CELL_SIZE) // 2
                screen.blit(CACHED_IMAGES['omnivore'], (screen_x, screen_y))
        
        for x, y in grid.carnivores:
            if grid.grid[y][x]:
                screen_x = x * CELL_SIZE - (45 - CELL_SIZE) // 2
                screen_y = y * CELL_SIZE - (45 - CELL_SIZE) // 2
                screen.blit(CACHED_IMAGES['carnivore'], (screen_x, screen_y))
        
        for x, y in grid.herbivores:
            if grid.grid[y][x]:
                screen_x = x * CELL_SIZE - (45 - CELL_SIZE) // 2
                screen_y = y * CELL_SIZE - (45 - CELL_SIZE) // 2
                screen.blit(CACHED_IMAGES['herbivore'], (screen_x, screen_y))

while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        camera.handle_input(event)

    # Update plants
    new_plants = []
    for plant in plants[:]:
        plant_child = plant.update()
        if plant_child:
            new_plants.append(plant_child)
    plants.extend(new_plants)
    
    # Random movement for animals
    def move_animal(animal):
        if random.random() < 0.05:  # 5% chance to move each frame
            # Random movement left or right
            move_x = random.choice([-1, 1]) * SQUARE_SIZE
            new_x = animal.x + move_x
            
            # Keep within grid bounds
            if 0 <= new_x < WINDOW_WIDTH - animal.size:
                animal.x = new_x
                animal.update()  # This will trigger the image flip

    # Update all animals with movement
    move_animal(omnivore1)
    move_animal(omnivore2)
    move_animal(carnivore1)
    move_animal(carnivore2)
    for herbivore in herbivores:
        move_animal(herbivore)

    # Draw
    world_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    ground.draw(world_surface)
    
    # Draw all objects
    for plant in plants:
        plant.draw(world_surface)
    for herbivore in herbivores:
        herbivore.draw(world_surface)
    carnivore1.draw(world_surface)
    carnivore2.draw(world_surface)
    omnivore1.draw(world_surface)
    omnivore2.draw(world_surface)
    
    # Apply camera transform and draw to screen
    screen.blit(camera.apply(world_surface), (0, 0))
    pygame.display.flip()

pygame.quit() 