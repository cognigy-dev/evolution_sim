import pygame
import math
import random
import os

# Colors
GREEN = (34, 139, 34)        # Dark green for main blades
LIGHT_GREEN = (144, 238, 144) # Light green for accent strokes
DARK_GREEN = (20, 120, 20)   # Darker green for base

class Plant:
    # Class variable to track total plants
    total_plants = 0
    
    def __init__(self, x, y):
        # Convert initial position to grid coordinates
        self.grid_x = x // 30  # SQUARE_SIZE = 30
        self.grid_y = y // 30
        self.size = 45  # 1.5x grid square size
        self.sway_time = 0
        self.age = 0
        self.can_spread = True
        self.spread_timer = random.randint(30, 60)
        self.maturity_age = 30
        
        # Increment total plant count
        Plant.total_plants += 1
        
        # Add flowers if population threshold reached
        self.has_flower = Plant.total_plants > 50 and random.random() < 0.02  # 2% chance after 50 plants
        self.has_accents = random.random() < 0.3
        
        # Generate clusters of grass blades
        self.clusters = []
        num_clusters = random.randint(3, 5)
        
        # If plant has flower, ensure one blade will be a flower stem
        self.flower_cluster = random.randint(0, num_clusters-1) if self.has_flower else -1
        self.flower_blade = random.randint(0, 5) if self.has_flower else -1
        
        for _ in range(num_clusters):
            cluster_x = random.randint(-15, 15)  # Increased spread for larger size
            cluster_y = random.randint(-15, 15)
            blades = []
            for _ in range(6):
                blades.append({
                    'length': random.randint(6, 15),  # Longer blades
                    'angle': random.uniform(0, 360),
                    'phase': random.uniform(0, 2),
                    'is_accent': random.random() < 0.1,
                    'is_flower_stem': self.has_flower and _ == self.flower_cluster and _ == self.flower_blade
                })
            self.clusters.append({
                'x': cluster_x,
                'y': cluster_y,
                'blades': blades
            })
    
    def __del__(self):
        # Decrement total plant count when a plant is removed
        Plant.total_plants -= 1
    
    def update(self):
        self.sway_time += 0.05
        self.age += 1

        if self.can_spread and self.age >= self.spread_timer:
            # Try to spread to adjacent grid squares
            spread_x = self.grid_x + random.choice([-1, 0, 1])
            spread_y = self.grid_y + random.choice([-1, 0, 1])
            
            # Check grid boundaries
            if 0 <= spread_x < 60 and 0 <= spread_y < 30:
                # Convert grid coordinates back to screen coordinates for new plant
                screen_x = spread_x * 30
                screen_y = spread_y * 30
                self.spread_timer = self.age + random.randint(30, 60)
                return Plant(screen_x, screen_y)
        
        return None
    
    def draw(self, surface):
        # Convert grid coordinates to screen coordinates and center in square
        base_x = self.grid_x * 30 - (self.size - 30) // 2
        base_y = self.grid_y * 30 - (self.size - 30) // 2
        
        for cluster in self.clusters:
            cluster_x = base_x + cluster['x']
            cluster_y = base_y + cluster['y']
            
            for blade in cluster['blades']:
                sway = math.sin(self.sway_time + blade['phase']) * 2
                current_angle = blade['angle'] + sway
                length = blade['length']
                
                end_x = cluster_x + math.cos(math.radians(current_angle)) * length
                end_y = cluster_y + math.sin(math.radians(current_angle)) * length
                
                # Draw base stroke (darker green)
                pygame.draw.line(surface, DARK_GREEN,
                               (int(cluster_x), int(cluster_y)),
                               (int(end_x), int(end_y)),
                               3)
                
                # Draw main blade color
                color = LIGHT_GREEN if blade['is_accent'] else GREEN
                pygame.draw.line(surface, color,
                               (int(cluster_x), int(cluster_y)),
                               (int(end_x), int(end_y)),
                               2)
                
                # Draw flower if this is a flower stem
                if blade['is_flower_stem']:
                    # Draw white flower (5 petals)
                    for petal in range(5):
                        petal_angle = math.radians(petal * 72)
                        petal_x = end_x + math.cos(petal_angle) * 2
                        petal_y = end_y + math.sin(petal_angle) * 2
                        pygame.draw.circle(surface, (255, 255, 255), 
                                        (int(petal_x), int(petal_y)), 2)
                    # Yellow center
                    pygame.draw.circle(surface, (255, 223, 0),
                                    (int(end_x), int(end_y)), 1) 