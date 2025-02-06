import pygame
import math
import random
import os

# Updated colors for a more natural look
DARK_GREEN = (25, 77, 30)     # Darker base green
MID_GREEN = (39, 89, 45)      # Medium green for main blades
LIGHT_GREEN = (52, 101, 58)   # Lighter green for accents
VERY_DARK_GREEN = (20, 55, 25) # Very dark green for base shadows

class Plant:
    # Class variable to track total plants
    total_plants = 0
    
    def __init__(self, x, y):
        # Convert initial position to grid coordinates
        self.grid_x = x // 30
        self.grid_y = y // 30
        self.size = 45  # 1.5x grid square size
        self.sway_time = random.uniform(0, 2 * math.pi)  # Random start phase
        self.age = 0
        self.can_spread = True
        self.spread_timer = random.randint(30, 60)
        
        # Increment total plant count
        Plant.total_plants += 1
        
        # Add flowers if population threshold reached
        self.has_flower = Plant.total_plants > 50 and random.random() < 0.02
        
        # Generate clusters of grass blades
        self.clusters = []
        num_clusters = random.randint(4, 6)  # More clusters for fuller look
        
        # Create main cluster in center
        self.create_cluster(0, 0, is_main=True)
        
        # Create surrounding clusters
        for _ in range(num_clusters - 1):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(5, 12)
            x = math.cos(angle) * dist
            y = math.sin(angle) * dist
            self.create_cluster(x, y, is_main=False)

    def create_cluster(self, x, y, is_main=False):
        num_blades = random.randint(6, 8) if is_main else random.randint(4, 6)
        blades = []
        
        # Add flower stem if this is the main cluster and plant has flower
        flower_blade = random.randint(0, num_blades-1) if is_main and self.has_flower else -1
        
        for i in range(num_blades):
            # More controlled angle distribution
            base_angle = (360 / num_blades) * i
            angle = base_angle + random.uniform(-20, 20)
            
            blades.append({
                'length': random.randint(12, 18) if is_main else random.randint(8, 14),
                'angle': angle,
                'phase': random.uniform(0, 2),
                'width': random.randint(2, 3),
                'color': random.choice([DARK_GREEN, MID_GREEN, LIGHT_GREEN]),
                'is_flower_stem': i == flower_blade
            })
        
        self.clusters.append({
            'x': x,
            'y': y,
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
        base_x = self.grid_x * 30 - (self.size - 30) // 2
        base_y = self.grid_y * 30 - (self.size - 30) // 2
        
        for cluster in self.clusters:
            cluster_x = base_x + self.size//2 + cluster['x']
            cluster_y = base_y + self.size//2 + cluster['y']
            
            # Draw shadow/base
            pygame.draw.circle(surface, VERY_DARK_GREEN, 
                             (int(cluster_x), int(cluster_y)), 4)
            
            for blade in cluster['blades']:
                # Calculate sway
                sway = math.sin(self.sway_time + blade['phase']) * 3
                current_angle = blade['angle'] + sway
                
                # Calculate end point with smooth curve
                length = blade['length']
                control_point_dist = length * 0.7
                
                start = pygame.Vector2(cluster_x, cluster_y)
                end = pygame.Vector2(
                    cluster_x + math.cos(math.radians(current_angle)) * length,
                    cluster_y + math.sin(math.radians(current_angle)) * length
                )
                
                # Draw blade with gradient effect
                points = []
                for t in range(0, 11):
                    t = t / 10
                    # Quadratic bezier curve
                    control = start.lerp(end, 0.5) + pygame.Vector2(
                        math.cos(math.radians(current_angle - 90)) * control_point_dist * 0.2,
                        math.sin(math.radians(current_angle - 90)) * control_point_dist * 0.2
                    )
                    point = start.lerp(control, t).lerp(control.lerp(end, t), t)
                    points.append((int(point.x), int(point.y)))
                
                if len(points) >= 2:
                    pygame.draw.lines(surface, blade['color'], False, points, blade['width'])
                
                # Draw flower if this is a flower stem
                if blade['is_flower_stem']:
                    # Draw white flower (5 petals)
                    for petal in range(5):
                        petal_angle = math.radians(petal * 72)
                        petal_x = end.x + math.cos(petal_angle) * 2
                        petal_y = end.y + math.sin(petal_angle) * 2
                        pygame.draw.circle(surface, (255, 255, 255), 
                                        (int(petal_x), int(petal_y)), 2)
                    # Yellow center
                    pygame.draw.circle(surface, (255, 223, 0),
                                    (int(end.x), int(end.y)), 1) 