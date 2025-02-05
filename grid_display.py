import pygame
import sys

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

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Grid Display")

def draw_grid():
    # Draw vertical lines
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, WINDOW_HEIGHT))
    
    # Draw horizontal lines
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WINDOW_WIDTH, y))

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Fill screen with white
    screen.fill(WHITE)
    
    # Draw the grid
    draw_grid()
    
    # Update the display
    pygame.display.flip() 