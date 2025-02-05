import pygame
import sys
import random
import math
from enum import Enum
from config import *

# Add this after the imports and before the pygame initialization
class Action(Enum):
    MOVE_TO_PLANT = "move_to_plant"
    MOVE_TO_HERBIVORE = "move_to_herbivore"
    MOVE_TO_OMNIVORE = "move_to_omnivore"
    MOVE_TO_CARNIVORE = "move_to_carnivore"
    FLEE_FROM_HERBIVORE = "flee_from_herbivore"
    FLEE_FROM_OMNIVORE = "flee_from_omnivore"
    FLEE_FROM_CARNIVORE = "flee_from_carnivore"
    RANDOM_MOVE = "random_move"
    STAY = "stay"

# Initialize Pygame
pygame.init()

# Calculate window dimensions
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Grid Display")

class Animal:
    def __init__(self, x, y, animal_type, is_offspring=False):
        self.x = x
        self.y = y
        self.animal_type = animal_type
        self.genes = self.generate_random_genes()
        self.reproduction_cooldown = REPRODUCTION_COOLDOWNS[animal_type] if is_offspring else 0
        self.hunger = 0
        self.age = 0
        self.stationary_count = 0  # Add counter for staying still
    
    def generate_random_genes(self):
        """Generate random genes for all possible vision configurations"""
        genes = {}
        # 5 possible distances (0-4) for each of the 4 types (plant, herbivore, omnivore, carnivore)
        # 0 means not visible
        for p in range(5):  # plant distances
            for h in range(5):  # herbivore distances
                for o in range(5):  # omnivore distances
                    for c in range(5):  # carnivore distances
                        key = (p, h, o, c)
                        # Only include STAY if there's an adjacent animal of same type (distance 1)
                        possible_actions = list(Action)
                        if self.animal_type == 'herbivore' and h != 1:
                            possible_actions.remove(Action.STAY)
                        elif self.animal_type == 'omnivore' and o != 1:
                            possible_actions.remove(Action.STAY)
                        elif self.animal_type == 'carnivore' and c != 1:
                            possible_actions.remove(Action.STAY)
                        genes[key] = random.choice(possible_actions)
        return genes
    
    def get_vision_key(self, vision_dict):
        """Convert vision distances to a key for gene lookup"""
        return (
            round(vision_dict.get('plant', 0)),
            round(vision_dict.get('herbivore', 0)),
            round(vision_dict.get('omnivore', 0)),
            round(vision_dict.get('carnivore', 0))
        )

    def feed(self):
        """Reset hunger when animal eats"""
        self.hunger = 0

    def mix_genes(self, parent1_genes, parent2_genes):
        """Mix genes from two parents with mutation chance"""
        mixed_genes = {}
        for key in parent1_genes.keys():
            # 50% chance to inherit from each parent for each gene
            if random.random() < 0.5:
                mixed_genes[key] = parent1_genes[key]
            else:
                mixed_genes[key] = parent2_genes[key]
        
        # 25% chance to mutate 10% of the genes
        if random.random() < 0.25:
            # Calculate number of genes to mutate (10% of total)
            num_mutations = max(1, int(len(mixed_genes) * 0.1))
            # Select random genes to mutate
            mutation_keys = random.sample(list(mixed_genes.keys()), num_mutations)
            
            for key in mutation_keys:
                # Generate a new random action for this gene
                possible_actions = list(Action)
                if self.animal_type == 'herbivore' and key[1] != 1:
                    possible_actions.remove(Action.STAY)
                elif self.animal_type == 'omnivore' and key[2] != 1:
                    possible_actions.remove(Action.STAY)
                elif self.animal_type == 'carnivore' and key[3] != 1:
                    possible_actions.remove(Action.STAY)
                mixed_genes[key] = random.choice(possible_actions)
        
        return mixed_genes

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
        """Check if position is valid and has no animals (plants are ok)"""
        if not self.is_valid_position(x, y):
            return False
        cell = self.grid[y][x]
        return cell is None or cell == PLANT_TYPE

    def is_empty_for_plant(self, x, y):
        """Check if position is valid and has no plant (animals are ok)"""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] == None or isinstance(self.grid[y][x], Animal)

    def has_animal(self, x, y):
        """Check if position has an animal"""
        if not self.is_valid_position(x, y):
            return False
        return isinstance(self.grid[y][x], Animal)

    def add_plant(self, x, y):
        if self.is_empty_for_plant(x, y):
            # If there's an animal, keep it in the same cell
            existing_animal = self.grid[y][x] if isinstance(self.grid[y][x], Animal) else None
            self.grid[y][x] = PLANT_TYPE
            self.plants.add((x, y))
            # Put the animal back on top if there was one
            if existing_animal:
                self.grid[y][x] = existing_animal
            return True
        return False

    def add_animal(self, x, y, animal_type, is_offspring=False):
        if self.is_empty(x, y):
            animal = Animal(x, y, animal_type, is_offspring)
            self.grid[y][x] = animal
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
            if self.is_empty_for_plant(new_x, new_y):  # Changed from is_empty to is_empty_for_plant
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

    def calculate_distance(self, x1, y1, x2, y2):
        return round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    def get_vision(self, x, y, vision_radius=VISION_RADIUS):
        """Return closest distances to each type within vision radius"""
        vision = {'plant': 0, 'herbivore': 0, 'omnivore': 0, 'carnivore': 0}
        
        # Check all cells within vision radius
        for dy in range(-vision_radius, vision_radius + 1):
            for dx in range(-vision_radius, vision_radius + 1):
                new_x, new_y = x + dx, y + dy
                if not self.is_valid_position(new_x, new_y):
                    continue
                
                distance = self.calculate_distance(x, y, new_x, new_y)
                if distance > vision_radius:
                    continue

                cell = self.grid[new_y][new_x]
                if cell is None:
                    continue

                # Fix: Properly identify cell type
                cell_type = None
                if cell == PLANT_TYPE:
                    cell_type = PLANT_TYPE
                elif isinstance(cell, Animal):
                    cell_type = cell.animal_type

                if cell_type and cell_type in vision:
                    current_dist = vision[cell_type]
                    if current_dist == 0 or distance < current_dist:
                        vision[cell_type] = distance

        return vision

    def move_towards(self, x, y, target_x, target_y):
        """Move one step towards target"""
        dx = target_x - x
        dy = target_y - y
        
        # Move in direction of larger difference
        if abs(dx) > abs(dy):
            dx = 1 if dx > 0 else -1
            dy = 0
        else:
            dx = 0
            dy = 1 if dy > 0 else -1
            
        new_x = x + dx
        new_y = y + dy
        
        if self.is_valid_position(new_x, new_y):
            return new_x, new_y
        return x, y

    def move_away(self, x, y, target_x, target_y):
        """Move one step away from target"""
        dx = x - target_x
        dy = y - target_y
        
        # Move in direction of larger difference
        if abs(dx) > abs(dy):
            dx = 1 if dx > 0 else -1
            dy = 0
        else:
            dx = 0
            dy = 1 if dy > 0 else -1
            
        new_x = x + dx
        new_y = y + dy
        
        if self.is_valid_position(new_x, new_y):
            return new_x, new_y
        return x, y

    def random_move(self, x, y):
        """Make a random move"""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y) and self.is_empty(new_x, new_y):
                return new_x, new_y
        
        return x, y  # Stay in place if no valid move

    def find_closest_of_type(self, x, y, vision_dict, target_type):
        """Find the closest entity of target_type within vision"""
        closest_dist = float('inf')
        closest_pos = None
        
        vision_radius = 4
        for dy in range(-vision_radius, vision_radius + 1):
            for dx in range(-vision_radius, vision_radius + 1):
                new_x, new_y = x + dx, y + dy
                if not self.is_valid_position(new_x, new_y):
                    continue
                
                cell = self.grid[new_y][new_x]
                if cell is None:
                    continue

                # Check if it's the type we're looking for
                if (target_type == PLANT_TYPE and cell == PLANT_TYPE) or \
                   (isinstance(cell, Animal) and cell.animal_type == target_type):
                    dist = self.calculate_distance(x, y, new_x, new_y)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_pos = (new_x, new_y)
        
        return closest_pos

    def apply_move(self, x, y, new_x, new_y, animal_type):
        """Move animal to new position if possible"""
        if not self.is_valid_position(new_x, new_y):
            return False

        # Get the animal at the target position (if any)
        target_animal = self.grid[new_y][new_x]
        
        # Get the moving animal
        animal = self.grid[y][x]
        animal.x, animal.y = new_x, new_y
            
        # Handle plant eating - herbivores and omnivores can eat plants
        if self.grid[new_y][new_x] == PLANT_TYPE:
            if animal_type in ['herbivore', 'omnivore']:
                # Only herbivores and omnivores eat and remove plants
                self.plants.remove((new_x, new_y))
                animal.feed()  # Reset hunger
                print(f"{animal_type} ate a plant at ({new_x}, {new_y})")
        
        # If there's already an animal, cancel move
        elif isinstance(target_animal, Animal):
            return False
        
        # Update grid and sets
        self.grid[new_y][new_x] = animal
        self.grid[y][x] = None
        
        # Update the appropriate set
        if animal_type == 'herbivore':
            self.herbivores.remove((x, y))
            self.herbivores.add((new_x, new_y))
        elif animal_type == 'carnivore':
            self.carnivores.remove((x, y))
            self.carnivores.add((new_x, new_y))
        elif animal_type == 'omnivore':
            self.omnivores.remove((x, y))
            self.omnivores.add((new_x, new_y))
        
        return True

    def find_parent_nearby(self, x, y, animal_type):
        """Find a potential parent of the same type at distance 1"""
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y):
                cell = self.grid[new_y][new_x]
                if isinstance(cell, Animal) and cell.animal_type == animal_type:
                    return cell
        return None

    def create_offspring(self, x, y, parent1, parent2, animal_type):
        """Create a new animal with mixed genes from parents"""
        offspring = Animal(x, y, animal_type, is_offspring=True)
        offspring.genes = offspring.mix_genes(parent1.genes, parent2.genes)
        return offspring

    def update_animals(self):
        """Update all animals based on their genes and vision"""
        all_animals = list(self.herbivores) + list(self.carnivores) + list(self.omnivores)
        random.shuffle(all_animals)
        
        # First check for deaths from hunger and age
        for x, y in list(all_animals):
            if not self.grid[y][x]:  # Skip if already removed
                continue
            
            animal = self.grid[y][x]
            animal.hunger += 1
            animal.age += 1  # Increment age
            
            # Let herbivores and omnivores eat plants they're standing on
            if (animal.animal_type in ['herbivore', 'omnivore']) and (x, y) in self.plants:
                self.plants.remove((x, y))
                animal.feed()
                print(f"{animal.animal_type} at ({x}, {y}) ate a plant it was standing on")
            
            # Check if animal dies from hunger or age
            if animal.hunger >= HUNGER_DEATH or animal.age >= AGE_DEATH:
                death_cause = "hunger" if animal.hunger >= HUNGER_DEATH else "old age"
                print(f"{animal.animal_type} at ({x}, {y}) died from {death_cause}")
                self.grid[y][x] = None
                if animal.animal_type == 'herbivore':
                    self.herbivores.remove((x, y))
                elif animal.animal_type == 'carnivore':
                    self.carnivores.remove((x, y))
                elif animal.animal_type == 'omnivore':
                    self.omnivores.remove((x, y))
                continue

        # Then handle reproduction
        for x, y in list(all_animals):
            if not self.grid[y][x]:  # Skip if animal was eaten
                continue
                
            animal = self.grid[y][x]
            
            # Decrease reproduction cooldown if it's active
            if animal.reproduction_cooldown > 0:
                animal.reproduction_cooldown -= 1
                continue  # Skip reproduction if on cooldown
            
            vision = self.get_vision(x, y)
            
            # Check for reproduction (when same type is at distance 1)
            if ((animal.animal_type == 'herbivore' and vision['herbivore'] == 1) or
                (animal.animal_type == 'omnivore' and vision['omnivore'] == 1) or
                (animal.animal_type == 'carnivore' and vision['carnivore'] == 1)):
                
                # Find the other parent
                other_parent = self.find_parent_nearby(x, y, animal.animal_type)
                if not other_parent:
                    continue
                
                # Find empty neighboring cells for offspring
                empty_neighbors = []
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if self.is_valid_position(new_x, new_y) and self.is_empty(new_x, new_y):
                        empty_neighbors.append((new_x, new_y))
                
                # Create offspring in random empty neighbor cell
                if empty_neighbors:
                    offspring_x, offspring_y = random.choice(empty_neighbors)
                    offspring = self.create_offspring(offspring_x, offspring_y, animal, other_parent, animal.animal_type)
                    self.grid[offspring_y][offspring_x] = offspring
                    
                    if animal.animal_type == 'herbivore':
                        self.herbivores.add((offspring_x, offspring_y))
                    elif animal.animal_type == 'carnivore':
                        self.carnivores.add((offspring_x, offspring_y))
                    elif animal.animal_type == 'omnivore':
                        self.omnivores.add((offspring_x, offspring_y))
                    
                    print(f"New {animal.animal_type} born at ({offspring_x}, {offspring_y}) with mixed genes")
                    animal.reproduction_cooldown = REPRODUCTION_COOLDOWNS[animal.animal_type]
                    other_parent.reproduction_cooldown = REPRODUCTION_COOLDOWNS[other_parent.animal_type]
        
        # Then handle eating
        for x, y in list(self.omnivores):
            if not self.grid[y][x]:  # Skip if dead
                continue
            animal = self.grid[y][x]
            vision = self.get_vision(x, y)
            
            # Track if omnivore ate something this turn
            ate_something = False
            if vision['herbivore'] == 1 or vision['carnivore'] == 1:
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if self.is_valid_position(new_x, new_y):
                        target = self.grid[new_y][new_x]
                        if isinstance(target, Animal):
                            if target.animal_type == 'herbivore':
                                self.herbivores.remove((new_x, new_y))
                                self.grid[new_y][new_x] = None
                                animal.feed()  # Reset hunger when eating
                                print(f"Omnivore at ({x}, {y}) ate a herbivore at ({new_x}, {new_y})")
                                ate_something = True
                                break
                            elif target.animal_type == 'carnivore':
                                self.carnivores.remove((new_x, new_y))
                                self.grid[new_y][new_x] = None
                                animal.feed()  # Reset hunger when eating
                                print(f"Omnivore at ({x}, {y}) ate a carnivore at ({new_x}, {new_y})")
                                ate_something = True
                                break

        # Then let carnivores eat herbivores
        for x, y in list(self.carnivores):
            if not self.grid[y][x]:  # Skip if dead
                continue
            animal = self.grid[y][x]
            vision = self.get_vision(x, y)
            
            # Track if carnivore ate something this turn
            ate_something = False
            if vision['herbivore'] == 1:
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if self.is_valid_position(new_x, new_y):
                        target = self.grid[new_y][new_x]
                        if isinstance(target, Animal) and target.animal_type == 'herbivore':
                            self.herbivores.remove((new_x, new_y))
                            self.grid[new_y][new_x] = None
                            animal.feed()  # Reset hunger when eating
                            print(f"Carnivore at ({x}, {y}) ate a herbivore at ({new_x}, {new_y})")
                            ate_something = True
                            break
        
        # Then proceed with normal movement
        for x, y in all_animals:
            # Skip if animal was eaten
            if not self.grid[y][x]:
                continue
                
            animal = self.grid[y][x]
            vision = self.get_vision(x, y)
            vision_key = animal.get_vision_key(vision)
            action = animal.genes[vision_key]
            
            # Force random move if stayed still too long
            if animal.stationary_count >= 3:
                action = Action.RANDOM_MOVE
                print(f"{animal.animal_type} at ({x},{y}) forced to move after staying still too long")
            
            # Debug print
            print(f"{animal.animal_type} at ({x},{y}) sees {vision}")
            print(f"Vision key: {vision_key}")
            print(f"Chose action: {action}")
            
            # Check if STAY is valid (only if same type is at distance 1)
            if action == Action.STAY:
                same_type_nearby = False
                if animal.animal_type == 'herbivore' and vision['herbivore'] == 1:
                    same_type_nearby = True
                elif animal.animal_type == 'omnivore' and vision['omnivore'] == 1:
                    same_type_nearby = True
                elif animal.animal_type == 'carnivore' and vision['carnivore'] == 1:
                    same_type_nearby = True
                
                if not same_type_nearby:
                    # If STAY is not valid, do a random move instead
                    action = Action.RANDOM_MOVE
            
            new_x, new_y = x, y  # Default to current position
            
            # Handle different actions
            if action == Action.MOVE_TO_PLANT:
                target = self.find_closest_of_type(x, y, vision, PLANT_TYPE)
                if target:
                    new_x, new_y = self.move_towards(x, y, *target)
            
            elif action == Action.MOVE_TO_HERBIVORE:
                target = self.find_closest_of_type(x, y, vision, 'herbivore')
                if target:
                    new_x, new_y = self.move_towards(x, y, *target)
            
            elif action == Action.MOVE_TO_OMNIVORE:
                target = self.find_closest_of_type(x, y, vision, 'omnivore')
                if target:
                    new_x, new_y = self.move_towards(x, y, *target)
            
            elif action == Action.MOVE_TO_CARNIVORE:
                target = self.find_closest_of_type(x, y, vision, 'carnivore')
                if target:
                    new_x, new_y = self.move_towards(x, y, *target)
            
            elif action == Action.FLEE_FROM_HERBIVORE:
                target = self.find_closest_of_type(x, y, vision, 'herbivore')
                if target:
                    new_x, new_y = self.move_away(x, y, *target)
            
            elif action == Action.FLEE_FROM_OMNIVORE:
                target = self.find_closest_of_type(x, y, vision, 'omnivore')
                if target:
                    new_x, new_y = self.move_away(x, y, *target)
            
            elif action == Action.FLEE_FROM_CARNIVORE:
                target = self.find_closest_of_type(x, y, vision, 'carnivore')
                if target:
                    new_x, new_y = self.move_away(x, y, *target)
            
            elif action == Action.RANDOM_MOVE:
                new_x, new_y = self.random_move(x, y)
            
            # Apply the move if it changed position
            if (new_x, new_y) != (x, y):
                success = self.apply_move(x, y, new_x, new_y, animal.animal_type)
                if success:
                    animal.stationary_count = 0  # Reset counter on successful move
                else:
                    animal.stationary_count += 1  # Increment if couldn't move
            else:
                animal.stationary_count += 1  # Increment if chose not to move

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
for _ in range(INITIAL_PLANTS):
    x = random.randint(0, GRID_WIDTH - 1)
    y = random.randint(0, GRID_HEIGHT - 1)
    grid.add_plant(x, y)

# Add random animals with specific counts for each type
animal_counts = {
    'herbivore': INITIAL_HERBIVORES,
    'carnivore': INITIAL_CARNIVORES,
    'omnivore': INITIAL_OMNIVORES
}

for animal_type, count in animal_counts.items():
    for _ in range(count):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if grid.add_animal(x, y, animal_type):
                break

# Main game loop
clock = pygame.time.Clock()
last_update = pygame.time.get_ticks()

while True:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Update plants and animals every second
    if current_time - last_update >= UPDATE_INTERVAL:
        grid.update_plants()
        grid.update_animals()
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