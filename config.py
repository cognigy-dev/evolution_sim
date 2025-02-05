# Grid Configuration
GRID_WIDTH = 60  # Number of cells in width
GRID_HEIGHT = 30  # Number of cells in height
CELL_SIZE = 30  # Size of each cell in pixels

# Initial Population
INITIAL_PLANTS = 15
INITIAL_HERBIVORES = 360
INITIAL_CARNIVORES = 100
INITIAL_OMNIVORES = 60

# Entity Types
ANIMAL_TYPES = ['herbivore', 'carnivore', 'omnivore']
PLANT_TYPE = 'plant'

# Animal Properties
VISION_RADIUS = 4  # How far animals can see
HUNGER_DEATH = 7  # Rounds without food before death
AGE_DEATH = 30  # Maximum age before death

# Reproduction Cooldowns
REPRODUCTION_COOLDOWNS = {
    'herbivore': 3,
    'carnivore': 6,
    'omnivore': 10
}

# Update Timing
UPDATE_INTERVAL = 1000  # Milliseconds between updates

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)  # Forest green for plants
BLUE = (65, 105, 225)  # Omnivores
RED = (220, 20, 60)    # Carnivores
YELLOW = (218, 165, 32)  # Herbivores 