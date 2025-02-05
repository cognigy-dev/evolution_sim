import pygame
import math
import os

class Creature3D:
    def __init__(self, x, y, z):  # Added z coordinate
        self.x = x
        self.y = y
        self.z = z  # Distance from viewer (depth)
        self.base_size = 60
        self.sway_time = 0
        
        # Load image same as before
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'assets', 'omnivore.png')
        
        try:
            self.base_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.base_image, (self.base_size, self.base_size))
            self.has_image = True
        except Exception as e:
            print(f"Error loading image: {e}")
            self.has_image = False
            
    def get_perspective_size(self):
        # Simulate perspective by making creatures smaller as they get further
        # z ranges from 0 (closest) to 1000 (furthest)
        scale = 1 - (self.z / 1200)  # Will be 1.0 at z=0, and 0.17 at z=1000
        return int(self.base_size * scale)
    
    def get_shadow_offset(self):
        # Shadow gets more offset and transparent as z increases
        shadow_y = 10 + (self.z * 0.05)  # Shadow drops lower for distant objects
        shadow_alpha = 255 - (self.z * 0.2)  # Shadow fades with distance
        return shadow_y, max(0, min(255, shadow_alpha))
    
    def update(self):
        # Example 3D movement
        self.sway_time += 0.1
        
        # Creatures could move in 3D space
        self.z += math.sin(self.sway_time * 0.5) * 0.5  # Gentle forward/back motion
        
        # Could add more complex 3D movements:
        # self.x += math.cos(self.sway_time) * 2
        # self.y += math.sin(self.sway_time * 0.7) * 1
    
    def draw(self, surface):
        if not self.has_image:
            return
            
        # Calculate perspective size
        size = self.get_perspective_size()
        scaled_image = pygame.transform.scale(self.base_image, (size, size))
        
        # Add hover effect that's more pronounced for closer objects
        hover = math.sin(self.sway_time) * (1.5 * (1 - self.z/1000))
        
        # Calculate shadow
        shadow_y, shadow_alpha = self.get_shadow_offset()
        
        # Create shadow (oval that gets more elongated with distance)
        shadow_surface = pygame.Surface((size, size//2), pygame.SRCALPHA)
        shadow_width = size * 0.8
        shadow_height = size * 0.2 * (1 + self.z/500)  # More elongated with distance
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha),
                          (0, 0, shadow_width, shadow_height))
        
        # Draw shadow first
        surface.blit(shadow_surface,
                    (self.x - shadow_width//2,
                     self.y - shadow_height//2 + shadow_y))
        
        # Then draw creature
        surface.blit(scaled_image, 
                    (self.x - size//2,
                     self.y - size//2 + hover))

class Herbivore3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z  # Distance from viewer
        self.size = 60
        self.sway_time = 0
        
        # Load the herbivore image - using absolute path from script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'assets', 'herbivore.png')
        
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
            self.has_image = True
        except Exception as e:
            print(f"Error loading herbivore image from {image_path}: {e}")
            self.has_image = False
    
    def update(self):
        self.sway_time += 0.08  # Slightly slower movement than omnivore
    
    def draw(self, surface):
        if not self.has_image:
            return
            
        # Calculate hover effect - gentler for herbivore
        hover = math.sin(self.sway_time) * 2
        
        # Calculate perspective scale (things get smaller as they get further)
        scale = 1 - (self.z / 1200)  # Will be 1.0 at z=0, and 0.17 at z=1000
        size = int(self.size * scale)
        
        if size <= 0:
            return
            
        # Scale image based on distance
        scaled_image = pygame.transform.scale(self.image, (size, size))
        
        # Draw the image centered at x,y with hover effect
        surface.blit(scaled_image, 
                    (self.x - size//2,
                     self.y - size//2 + hover))

# Example usage:
"""
# Create creatures at different depths
creatures = [
    Creature3D(400, 300, 0),    # Front
    Creature3D(300, 250, 200),  # Mid-left
    Creature3D(500, 250, 200),  # Mid-right
    Creature3D(400, 200, 400),  # Back
]

# In game loop:
for creature in sorted(creatures, key=lambda c: c.z, reverse=True):
    # Draw back to front
    creature.draw(screen)
""" 