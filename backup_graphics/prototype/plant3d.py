import pygame
import math
import random

class Plant3D:
    # Class variable to track total plants
    total_plants = 0
    
    def __init__(self, x, y, z, is_child=False):
        self.x = x
        self.y = y
        self.z = z
        self.size = 30
        self.sway_time = 0
        self.age = 0
        self.can_spread = not is_child
        self.spread_timer = random.randint(30, 60)
        self.maturity_age = 30  # Changed from 60 to 30 to match original
        
        # Increment total plant count
        Plant3D.total_plants += 1
        
        # Add flowers if population threshold reached
        self.has_flower = Plant3D.total_plants > 50 and random.random() < 0.02  # 2% chance after 50 plants
        self.has_accents = random.random() < 0.3
        
        # Generate clusters of grass blades
        self.clusters = []
        num_clusters = 3 if is_child else 5  # Fixed numbers instead of random
        
        # If plant has flower, ensure one blade will be a flower stem
        self.flower_cluster = random.randint(0, num_clusters-1) if self.has_flower else -1
        self.flower_blade = random.randint(0, 5) if self.has_flower else -1
        
        for i in range(num_clusters):
            cluster_x = random.randint(-12, 12)
            cluster_z = random.randint(-12, 12)
            blades = []
            for j in range(6):
                blades.append({
                    'length': random.randint(4, 10),
                    'angle': random.uniform(0, 360),
                    'phase': random.uniform(0, 2),
                    'is_accent': self.has_accents and random.random() < 0.1,
                    'is_flower_stem': self.has_flower and i == self.flower_cluster and j == self.flower_blade
                })
            self.clusters.append({
                'x': cluster_x,
                'z': cluster_z,
                'blades': blades
            })
    
    def __del__(self):
        # Decrement total plant count when a plant is removed
        Plant3D.total_plants -= 1

    def get_perspective_size(self, max_depth):
        # Scale based on distance from viewer
        scale = 1 - (self.z / (max_depth * 1.2))
        return max(1, int(self.size * scale))

    def update(self):
        self.sway_time += 0.05
        self.age += 2  # Age faster
        
        if self.can_spread:
            if self.age >= self.spread_timer:
                spread_distance = random.randint(20, 35)
                spread_angle = random.uniform(0, 2 * math.pi)
                
                new_x = self.x + math.cos(spread_angle) * spread_distance
                new_z = self.z + math.sin(spread_angle) * spread_distance
                
                if -600 <= new_x <= 600 and 50 <= new_z <= 600:
                    self.spread_timer = self.age + random.randint(20, 40)  # Spread more frequently
                    return Plant3D(new_x, self.y, new_z, is_child=True)
        elif self.age >= self.maturity_age:
            self.can_spread = True
            self.spread_timer = self.age + random.randint(20, 40)
        
        return None

    def draw(self, surface, grid):
        # Get base position from grid
        base_x, base_y = grid.get_grid_position(self.x, grid.horizon_y + 300, self.z)
        size_scale = 1 - (self.z / (grid.grid_depth * grid.cell_size * 1.2))
        
        for cluster in self.clusters:
            cluster_x = base_x + cluster['x'] * size_scale
            cluster_z = self.z + cluster['z']
            _, cluster_y = grid.get_grid_position(self.x, grid.horizon_y + 300, cluster_z)
            
            for blade in cluster['blades']:
                sway = math.sin(self.sway_time + blade['phase']) * (1.5 * size_scale)
                current_angle = blade['angle'] + sway
                length = blade['length'] * size_scale
                
                end_x = cluster_x + math.cos(math.radians(current_angle)) * length
                end_y = cluster_y + math.sin(math.radians(current_angle)) * length
                
                # Draw base stroke (darker green)
                color = (20, 120, 20, int(255 * size_scale))  # Add transparency based on distance
                pygame.draw.line(surface, color,
                               (int(cluster_x), int(cluster_y)),
                               (int(end_x), int(end_y)),
                               max(1, int(3 * size_scale)))
                
                # Draw main blade color
                color = (144, 238, 144) if blade['is_accent'] else (34, 139, 34)
                color = (*color, int(255 * size_scale))  # Add transparency
                pygame.draw.line(surface, color,
                               (int(cluster_x), int(cluster_y)),
                               (int(end_x), int(end_y)),
                               max(1, int(2 * size_scale)))
                
                # Draw flower if this is a flower stem
                if blade['is_flower_stem']:
                    flower_size = max(1, int(2 * size_scale))
                    for petal in range(5):
                        petal_angle = math.radians(petal * 72)
                        petal_x = end_x + math.cos(petal_angle) * flower_size
                        petal_y = end_y + math.sin(petal_angle) * flower_size
                        pygame.draw.circle(surface, (255, 255, 255, int(255 * size_scale)), 
                                        (int(petal_x), int(petal_y)), flower_size)
                    pygame.draw.circle(surface, (255, 223, 0, int(255 * size_scale)),
                                    (int(end_x), int(end_y)), max(1, int(flower_size * 0.5))) 