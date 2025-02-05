import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 60  # Number of cells in width
GRID_HEIGHT = 30  # Number of cells in height
CELL_SIZE = 30  # Size of each cell in pixels
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)  # Forest green for plants
BLUE = (65, 105, 225)  # Omnivores
RED = (220, 20, 60)    # Carnivores
YELLOW = (218, 165, 32)  # Herbivores

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Grid Display")

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.plants = set()  # Store plant coordinates
        self.omnivores = set()
        self.carnivores = set()
        self.herbivores = set()

    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_empty(self, x, y):
        return self.is_valid_position(x, y) and self.grid[y][x] is None

    def add_plant(self, x, y):
        if self.is_empty(x, y):
            self.grid[y][x] = 'plant'
            self.plants.add((x, y))
            return True
        return False

    def add_animal(self, x, y, animal_type):
        if self.is_empty(x, y):
            self.grid[y][x] = animal_type
            if animal_type == 'omnivore':
                self.omnivores.add((x, y))
            elif animal_type == 'carnivore':
                self.carnivores.add((x, y))
            elif animal_type == 'herbivore':
                self.herbivores.add((x, y))
            return True
        return False

    def get_empty_neighbors(self, x, y):
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if self.is_empty(new_x, new_y):
                neighbors.append((new_x, new_y))
        return neighbors

    def update_plants(self):
        new_plants = set()
        for plant_x, plant_y in self.plants:
            empty_neighbors = self.get_empty_neighbors(plant_x, plant_y)
            if empty_neighbors:
                new_x, new_y = random.choice(empty_neighbors)
                new_plants.add((new_x, new_y))
        
        # Add all new plants
        for x, y in new_plants:
            self.add_plant(x, y)

def draw_grid():
    # Draw vertical lines
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, WINDOW_HEIGHT))
    
    # Draw horizontal lines
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WINDOW_WIDTH, y))

def draw_plants(grid):
    for plant_x, plant_y in grid.plants:
        rect = pygame.Rect(
            plant_x * CELL_SIZE + 1,  # +1 to not overlap with grid lines
            plant_y * CELL_SIZE + 1,
            CELL_SIZE - 2,  # -2 to not overlap with grid lines
            CELL_SIZE - 2
        )
        pygame.draw.rect(screen, GREEN, rect)

def draw_animals(grid):
    # Draw omnivores
    for x, y in grid.omnivores:
        rect = pygame.Rect(
            x * CELL_SIZE + 1,
            y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        )
        pygame.draw.rect(screen, BLUE, rect)
    
    # Draw carnivores
    for x, y in grid.carnivores:
        rect = pygame.Rect(
            x * CELL_SIZE + 1,
            y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        )
        pygame.draw.rect(screen, RED, rect)
    
    # Draw herbivores
    for x, y in grid.herbivores:
        rect = pygame.Rect(
            x * CELL_SIZE + 1,
            y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        )
        pygame.draw.rect(screen, YELLOW, rect)

# Initialize grid and add initial plants
grid = Grid(GRID_WIDTH, GRID_HEIGHT)

# Add some random initial plants
INITIAL_PLANTS = 5
for _ in range(INITIAL_PLANTS):
    x = random.randint(0, GRID_WIDTH - 1)
    y = random.randint(0, GRID_HEIGHT - 1)
    grid.add_plant(x, y)

# Add random animals
INITIAL_ANIMALS = 3  # Number of each type of animal
animal_types = ['omnivore', 'carnivore', 'herbivore']

for animal_type in animal_types:
    for _ in range(INITIAL_ANIMALS):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if grid.add_animal(x, y, animal_type):
                break

# Main game loop
clock = pygame.time.Clock()
UPDATE_INTERVAL = 1000  # milliseconds between updates
last_update = pygame.time.get_ticks()

while True:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Update plants every second
    if current_time - last_update >= UPDATE_INTERVAL:
        grid.update_plants()
        last_update = current_time
    
    # Fill screen with white
    screen.fill(WHITE)
    
    # Draw everything
    draw_grid()
    draw_plants(grid)
    draw_animals(grid)
    
    # Update the display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(60) 