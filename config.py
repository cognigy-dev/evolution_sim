# Grid Configuration
GRID_WIDTH = 60  # Number of cells in width
GRID_HEIGHT = 30  # Number of cells in height
CELL_SIZE = 30  # Size of each cell in pixels

# Initial Population
INITIAL_PLANTS = 15
INITIAL_HERBIVORES = 250
INITIAL_CARNIVORES = 60
INITIAL_OMNIVORES = 60

# Entity Types
ANIMAL_TYPES = ['herbivore', 'carnivore', 'omnivore']
PLANT_TYPE = 'plant'

# Animal Properties
VISION_RADIUS = 4  # How far animals can see

# Death conditions for each type
HUNGER_DEATH = {
    'herbivore': 7,
    'carnivore': 40,
    'omnivore': 8
}

AGE_DEATH = {
    'herbivore': 40,
    'carnivore': 50,
    'omnivore': 30
}

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

# Add these new configuration parameters
SIMULATION_STEPS = 300  # Steps per simulation
NUMBER_OF_SIMULATIONS = 50  # Number of simulations to run per generation
TOP_PERFORMERS_TO_KEEP = 10  # Number of best animals to keep
TRAINING_GENERATIONS = 20  # Number of generations to train 