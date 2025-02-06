import pygame
import sys
import random
import math
from enum import Enum
from config import *  # Make sure this imports all config parameters first
import os
import json
from datetime import datetime
from graphics.ground import Ground
from graphics.plant import Plant
try:
    from graphics.omnivore import Omnivore
    from graphics.herbivore import Herbivore
    from graphics.carnivore import Carnivore
    GRAPHICS_AVAILABLE = True
except ImportError:
    print("Warning: Advanced graphics not available, falling back to simple shapes")
    GRAPHICS_AVAILABLE = False

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Verify all required constants are imported
required_constants = [
    'GRID_WIDTH', 'GRID_HEIGHT', 'CELL_SIZE',
    'INITIAL_PLANTS', 'INITIAL_HERBIVORES', 'INITIAL_CARNIVORES', 'INITIAL_OMNIVORES',
    'ANIMAL_TYPES', 'PLANT_TYPE',
    'VISION_RADIUS', 'HUNGER_DEATH', 'AGE_DEATH',
    'REPRODUCTION_COOLDOWNS',
    'UPDATE_INTERVAL',
    'WHITE', 'BLACK', 'GREEN', 'BLUE', 'RED', 'YELLOW',
    'SIMULATION_STEPS', 'NUMBER_OF_SIMULATIONS', 'TOP_PERFORMERS_TO_KEEP', 'TRAINING_GENERATIONS'
]

for const in required_constants:
    if not const in globals():
        raise NameError(f"Required constant {const} not found in config.py")

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
pygame.font.init()  # Initialize the font module
FONT = pygame.font.SysFont('Arial', 24)  # Create a font object

# Calculate window dimensions
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Grid Display")

class Animal:
    def __init__(self, x, y, animal_type, is_offspring=False, genes=None):
        self.x = x
        self.y = y
        self.animal_type = animal_type
        self.genes = genes if genes else self.generate_random_genes()
        self.reproduction_cooldown = REPRODUCTION_COOLDOWNS[animal_type] if is_offspring else 0
        self.hunger = 0
        self.age = 0
        self.stationary_count = 0
        # Add fitness tracking
        self.survival_time = 0
        self.offspring_count = 0
    
    def generate_random_genes(self):
        """Generate random genes for all possible vision configurations"""
        genes = {}
        vision_range = VISION_RADIUS[self.animal_type]
        
        # Generate genes based on type-specific vision radius
        for p in range(vision_range + 1):  # plant distances
            for h in range(vision_range + 1):  # herbivore distances
                for o in range(vision_range + 1):  # omnivore distances
                    for c in range(vision_range + 1):  # carnivore distances
                        key = (p, h, o, c)
                        # Create list of possible actions based on what's visible
                        possible_actions = []
                        
                        # Add movement actions only if target is visible
                        if p > 0:  # Plant is visible
                            possible_actions.append(Action.MOVE_TO_PLANT)
                        if h > 0:  # Herbivore is visible
                            possible_actions.append(Action.MOVE_TO_HERBIVORE)
                            possible_actions.append(Action.FLEE_FROM_HERBIVORE)
                        if o > 0:  # Omnivore is visible
                            possible_actions.append(Action.MOVE_TO_OMNIVORE)
                            possible_actions.append(Action.FLEE_FROM_OMNIVORE)
                        if c > 0:  # Carnivore is visible
                            possible_actions.append(Action.MOVE_TO_CARNIVORE)
                            possible_actions.append(Action.FLEE_FROM_CARNIVORE)
                        
                        possible_actions.append(Action.RANDOM_MOVE)
                        
                        if (self.animal_type == 'herbivore' and h == 1) or \
                           (self.animal_type == 'omnivore' and o == 1) or \
                           (self.animal_type == 'carnivore' and c == 1):
                            possible_actions.append(Action.STAY)
                        
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

    def add_animal(self, x, y, animal_type, is_offspring=False, genes=None):
        if self.is_empty(x, y):
            animal = Animal(x, y, animal_type, is_offspring, genes)
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

    def get_vision(self, x, y, animal_type):
        """Return closest distances to each type within vision radius"""
        vision_radius = VISION_RADIUS[animal_type]
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
            
            # Check if animal dies from hunger or age using type-specific values
            death_message = None
            if animal.hunger >= HUNGER_DEATH[animal.animal_type]:
                death_message = f"{animal.animal_type.upper()} DEATH at ({x}, {y}): Died from hunger after {animal.hunger} steps without food (limit: {HUNGER_DEATH[animal.animal_type]})"
            elif animal.age >= AGE_DEATH[animal.animal_type]:
                death_message = f"{animal.animal_type.upper()} DEATH at ({x}, {y}): Died from old age after living {animal.age} steps (limit: {AGE_DEATH[animal.animal_type]})"
            
            if death_message:
                print(death_message)
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
            
            # Skip reproduction if too hungry (hunger >= 50% of max)
            if animal.hunger >= HUNGER_DEATH[animal.animal_type] / 2:
                continue
            
            # Decrease reproduction cooldown if it's active
            if animal.reproduction_cooldown > 0:
                animal.reproduction_cooldown -= 1
                continue  # Skip reproduction if on cooldown
            
            vision = self.get_vision(x, y, animal.animal_type)
            
            # Check for reproduction (when same type is at distance 1)
            if ((animal.animal_type == 'herbivore' and vision['herbivore'] == 1) or
                (animal.animal_type == 'carnivore' and vision['carnivore'] == 1) or
                (animal.animal_type == 'omnivore' and vision['omnivore'] == 1)):
                
                # Find the other parent
                other_parent = self.find_parent_nearby(x, y, animal.animal_type)
                # Also check if other parent is too hungry
                if (not other_parent or 
                    other_parent.reproduction_cooldown > 0 or 
                    other_parent.hunger >= HUNGER_DEATH[other_parent.animal_type] / 2):
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
                    animal.offspring_count += 1
                    other_parent.offspring_count += 1
        
        # Then handle eating for omnivores
        for x, y in list(self.omnivores):
            if not self.grid[y][x]:  # Skip if dead
                continue
            animal = self.grid[y][x]
            vision = self.get_vision(x, y, animal.animal_type)
            
            # Only hunt if hungry enough (at least half of hunger death limit)
            is_hungry_enough = animal.hunger >= HUNGER_DEATH[animal.animal_type] / 2
            
            # Track if omnivore ate something this turn
            ate_something = False
            if vision['herbivore'] == 1 and is_hungry_enough:  # Changed to only check for herbivores
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if self.is_valid_position(new_x, new_y):
                        target = self.grid[new_y][new_x]
                        if isinstance(target, Animal) and target.animal_type == 'herbivore':
                            self.herbivores.remove((new_x, new_y))
                            self.grid[new_y][new_x] = None
                            animal.feed()  # Reset hunger when eating
                            print(f"Hungry omnivore at ({x}, {y}) ate a herbivore at ({new_x}, {new_y})")
                            ate_something = True
                            break

        # Then let carnivores eat herbivores and omnivores
        for x, y in list(self.carnivores):
            if not self.grid[y][x]:  # Skip if dead
                continue
            animal = self.grid[y][x]
            vision = self.get_vision(x, y, animal.animal_type)
            
            # Only hunt if hungry enough (at least half of hunger death limit)
            is_hungry_enough = animal.hunger >= HUNGER_DEATH[animal.animal_type] / 2
            
            # Track if carnivore ate something this turn
            ate_something = False
            if (vision['herbivore'] == 1 or vision['omnivore'] == 1) and is_hungry_enough:
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if self.is_valid_position(new_x, new_y):
                        target = self.grid[new_y][new_x]
                        if isinstance(target, Animal):
                            if target.animal_type == 'herbivore':
                                self.herbivores.remove((new_x, new_y))
                                self.grid[new_y][new_x] = None
                                animal.feed()  # Reset hunger when eating
                                print(f"Hungry carnivore at ({x}, {y}) ate a herbivore at ({new_x}, {new_y})")
                                ate_something = True
                                break
                            elif target.animal_type == 'omnivore':
                                self.omnivores.remove((new_x, new_y))
                                self.grid[new_y][new_x] = None
                                animal.feed()  # Reset hunger when eating
                                print(f"Hungry carnivore at ({x}, {y}) ate an omnivore at ({new_x}, {new_y})")
                                ate_something = True
                                break
        
        # Then proceed with normal movement
        for x, y in all_animals:
            # Skip if animal was eaten
            if not self.grid[y][x]:
                continue
                
            animal = self.grid[y][x]
            vision = self.get_vision(x, y, animal.animal_type)
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
    # Draw ground first using the Ground class
    ground = Ground(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)
    ground.draw(screen)
    
    # Draw grid lines with reduced opacity for a more subtle look
    grid_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(grid_surface, (*BLACK, 40), (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(grid_surface, (*BLACK, 40), (0, y), (WINDOW_WIDTH, y))
    screen.blit(grid_surface, (0, 0))

def draw_plants(grid):
    for plant_x, plant_y in grid.plants:
        # Use the Plant class instead of simple rectangles
        plant = Plant(plant_x * CELL_SIZE, plant_y * CELL_SIZE)
        plant.draw(screen)

def draw_animals(grid):
    if GRAPHICS_AVAILABLE:
        # Draw with advanced graphics
        for x, y in grid.omnivores:
            if grid.grid[y][x]:
                omnivore = Omnivore(x * CELL_SIZE, y * CELL_SIZE)
                omnivore.draw(screen)
        
        for x, y in grid.carnivores:
            if grid.grid[y][x]:
                carnivore = Carnivore(x * CELL_SIZE, y * CELL_SIZE)
                carnivore.draw(screen)
        
        for x, y in grid.herbivores:
            if grid.grid[y][x]:
                herbivore = Herbivore(x * CELL_SIZE, y * CELL_SIZE)
                herbivore.draw(screen)
    else:
        # Fall back to simple rectangles
        for x, y in grid.omnivores:
            rect = pygame.Rect(
                x * CELL_SIZE + 1,
                y * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
            pygame.draw.rect(screen, BLUE, rect)
        
        for x, y in grid.carnivores:
            rect = pygame.Rect(
                x * CELL_SIZE + 1,
                y * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
            pygame.draw.rect(screen, RED, rect)
        
        for x, y in grid.herbivores:
            rect = pygame.Rect(
                x * CELL_SIZE + 1,
                y * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
            pygame.draw.rect(screen, YELLOW, rect)

def draw_simulation_counter(generation, simulation, step=None, total_steps=SIMULATION_STEPS):
    """Draw the current generation, simulation numbers and time progress"""
    gen_sim_text = f"Generation: {generation + 1}, Simulation: {simulation + 1}"
    text_surface = FONT.render(gen_sim_text, True, BLACK)
    screen.blit(text_surface, (10, 10))  # Position in top-left corner
    
    if step is not None:
        # Add progress information
        progress_text = f"Step: {step}/{total_steps} ({(step/total_steps*100):.1f}%)"
        progress_surface = FONT.render(progress_text, True, BLACK)
        screen.blit(progress_surface, (10, 40))  # Position below generation/simulation counter

def run_simulation(initial_genes=None, visualize=False, generation=0, simulation=0):
    """Run a single simulation and return the results"""
    if visualize:
        # Clear screen and show "Starting new simulation" message
        screen.fill(WHITE)
        start_text = f"Starting Generation {generation + 1}, Simulation {simulation + 1}"
        text_surface = FONT.render(start_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)
    
    # Create a new grid for this simulation
    grid = Grid(GRID_WIDTH, GRID_HEIGHT)
    
    # Initialize grid with plants and animals
    for _ in range(INITIAL_PLANTS):
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        grid.add_plant(x, y)
    
    animal_counts = {
        'herbivore': INITIAL_HERBIVORES,
        'carnivore': INITIAL_CARNIVORES,
        'omnivore': INITIAL_OMNIVORES
    }
    
    all_animals = []
    for animal_type, count in animal_counts.items():
        for i in range(count):
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                # Fix the gene assignment logic
                genes = None
                if initial_genes and initial_genes[animal_type]:
                    # Use modulo to cycle through available genes
                    gene_index = i % len(initial_genes[animal_type])
                    genes = initial_genes[animal_type][gene_index]
                
                if grid.add_animal(x, y, animal_type, genes=genes):
                    if isinstance(grid.grid[y][x], Animal):
                        all_animals.append(grid.grid[y][x])
                    break
    
    # Run simulation for specified steps or until all animals die
    for step in range(SIMULATION_STEPS):
        grid.update_plants()
        grid.update_animals()
        
        # Check if all animals are dead
        all_animals_dead = len(grid.herbivores) == 0 and \
                          len(grid.carnivores) == 0 and \
                          len(grid.omnivores) == 0
        
        if all_animals_dead:
            print(f"All animals died in simulation {simulation} at step {step}")
            break
        
        # Update survival time for living animals
        for animal in all_animals:
            if animal.age is not None:  # Check if animal is still alive
                animal.survival_time += 1
        
        # Visualize if requested
        if visualize:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            screen.fill(WHITE)
            draw_grid()
            draw_plants(grid)
            draw_animals(grid)
            draw_simulation_counter(generation, simulation, step)
            pygame.display.flip()
            pygame.time.wait(50)
    
    if visualize and not all_animals_dead:
        # Only show completion message if simulation ran full course
        screen.fill(WHITE)
        end_text = f"Generation {generation + 1}, Simulation {simulation + 1} Complete"
        text_surface = FONT.render(end_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)
    
    # Calculate results
    results = []
    for animal in all_animals:
        results.append((animal, animal.survival_time))
    
    return results

def save_simulation_results(simulation_count, type_results_dict, best_genes):
    """Save simulation results and best genes to files"""
    # Create results directory if it doesn't exist
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = f"simulation_results/{timestamp}"
    os.makedirs(base_dir, exist_ok=True)
    
    # Save simulation statistics
    stats = {}
    for animal_type, type_results in type_results_dict.items():
        if type_results:
            survival_times = [survival for _, survival in type_results]
            stats[animal_type] = {
                "avg_survival": sum(survival_times) / len(survival_times),
                "max_survival": max(survival_times),
                "total_animals": len(type_results),
                "top_3_survival_times": sorted(survival_times, reverse=True)[:3]
            }
    
    with open(f"{base_dir}/simulation_{simulation_count}_stats.json", 'w') as f:
        json.dump(stats, f, indent=4)
    
    # Save top 3 genes for each type
    for animal_type in ANIMAL_TYPES:
        if best_genes[animal_type]:
            # Convert genes to serializable format (convert Enum to string)
            serializable_genes = []
            for genes in best_genes[animal_type][:3]:  # Save top 3
                serializable_gene = {
                    str(key): action.name for key, action in genes.items()
                }
                serializable_genes.append(serializable_gene)
            
            with open(f"{base_dir}/best_genes_{animal_type}_{simulation_count}.json", 'w') as f:
                json.dump(serializable_genes, f, indent=4)

def load_genes(filepath):
    """Load genes from a file and convert back to proper format"""
    with open(filepath, 'r') as f:
        serialized_genes = json.load(f)
    
    # Convert back to proper format
    genes = []
    for serialized_gene in serialized_genes:
        gene = {}
        for key_str, action_str in serialized_gene.items():
            # Convert string tuple to actual tuple
            key = tuple(map(int, key_str.strip('()').split(', ')))
            # Convert string to Action enum
            action = Action[action_str]
            gene[key] = action
        genes.append(gene)
    
    return genes

# Modify main game loop to use trained genes
if __name__ == "__main__":
    print("Starting continuous simulation and gathering best genes...")
    
    best_genes = {
        'herbivore': [],
        'carnivore': [],
        'omnivore': []
    }
    
    simulation_count = 0
    while True:
        # Run a single simulation with visualization
        results = run_simulation(
            initial_genes=best_genes if simulation_count > 0 else None,
            visualize=True,
            generation=0,
            simulation=simulation_count
        )
        
        # Collect results for all types
        type_results_dict = {}
        next_generation_genes = {
            'herbivore': [],
            'carnivore': [],
            'omnivore': []
        }
        
        for animal_type in ANIMAL_TYPES:
            type_results = [(animal, survival_time) for animal, survival_time in results 
                          if animal.animal_type == animal_type]
            type_results.sort(key=lambda x: x[1], reverse=True)
            type_results_dict[animal_type] = type_results
            
            if type_results:
                # Get the best performers from this simulation
                best_performers = type_results[:TOP_PERFORMERS_TO_KEEP]
                
                # For each new gene set we need
                for _ in range(TOP_PERFORMERS_TO_KEEP):
                    # Take a random one of the best performers' genes
                    base_genes = random.choice(best_performers)[0].genes.copy()
                    
                    # 25% chance for mutation
                    if random.random() < 0.25:
                        # Mutate 10% of the genes
                        num_mutations = max(1, int(len(base_genes) * 0.1))
                        mutation_keys = random.sample(list(base_genes.keys()), num_mutations)
                        
                        for key in mutation_keys:
                            p, h, o, c = key
                            possible_actions = []
                            
                            # Build list of possible actions based on what's visible
                            if p > 0:
                                possible_actions.append(Action.MOVE_TO_PLANT)
                            if h > 0:
                                possible_actions.append(Action.MOVE_TO_HERBIVORE)
                                possible_actions.append(Action.FLEE_FROM_HERBIVORE)
                            if o > 0:
                                possible_actions.append(Action.MOVE_TO_OMNIVORE)
                                possible_actions.append(Action.FLEE_FROM_OMNIVORE)
                            if c > 0:
                                possible_actions.append(Action.MOVE_TO_CARNIVORE)
                                possible_actions.append(Action.FLEE_FROM_CARNIVORE)
                            
                            possible_actions.append(Action.RANDOM_MOVE)
                            
                            if ((animal_type == 'herbivore' and h == 1) or
                                (animal_type == 'omnivore' and o == 1) or
                                (animal_type == 'carnivore' and c == 1)):
                                possible_actions.append(Action.STAY)
                            
                            base_genes[key] = random.choice(possible_actions)
                    
                    next_generation_genes[animal_type].append(base_genes)
                
                # Update best genes for next simulation
                best_genes[animal_type] = next_generation_genes[animal_type]
                
                # Print stats
                avg_survival = sum(survival for _, survival in type_results) / len(type_results)
                max_survival = max(survival for _, survival in type_results)
                print(f"\nSimulation {simulation_count} - {animal_type}:")
                print(f"Avg Survival Time: {avg_survival:.2f}")
                print(f"Best Survival Time: {max_survival}")
                print(f"Total animals: {len(type_results)}")
        
        # Save simulation results and best genes
        save_simulation_results(simulation_count, type_results_dict, best_genes)
        
        simulation_count += 1
        print(f"\nStarting next simulation with mutated genes from top {TOP_PERFORMERS_TO_KEEP} performers\n")
        
        # Handle quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() 