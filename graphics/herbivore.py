import pygame
import math
import os
import random
from trail import Trail

class Herbivore(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.grid_x = x // 30
        self.grid_y = y // 30
        self.size = 60
        self.direction = 'right'
        
        # Movement and trail properties
        self.moving = False
        self.trail = Trail(8)  # Create trail with 8 positions
        self.prev_x = self.grid_x
        self.prev_y = self.grid_y
        self.lerp_t = 0  # Interpolation progress
        self.move_speed = 0.15  # Movement speed
        
        # Load base image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            self.base_image = pygame.transform.scale(
                pygame.image.load(os.path.join(script_dir, 'assets', 'herbivore.png')).convert_alpha(),
                (self.size, self.size)
            )
            self.image = self.base_image
            self.has_image = True
        except Exception as e:
            print(f"Error loading herbivore image: {e}")
            self.has_image = False

    def update(self):
        if self.lerp_t >= 1.0:  # If not currently moving
            if random.random() < 0.03:  # 3% chance to move
                direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                new_grid_x = self.grid_x + direction[0]
                new_grid_y = self.grid_y + direction[1]
                
                # Update facing direction
                if direction[0] > 0:
                    self.direction = 'right'
                elif direction[0] < 0:
                    self.direction = 'left'
                
                # Check grid boundaries
                if 0 <= new_grid_x < 60 and 0 <= new_grid_y < 30:
                    self.prev_x = self.grid_x
                    self.prev_y = self.grid_y
                    self.grid_x = new_grid_x
                    self.grid_y = new_grid_y
                    self.lerp_t = 0
                    self.moving = True
                    if self.has_image:
                        self.image = pygame.transform.flip(self.base_image, self.direction == 'left', False)
        else:
            # Interpolate movement
            self.lerp_t = min(1.0, self.lerp_t + self.move_speed)
            
            # Calculate current screen position
            current_x = self.prev_x + (self.grid_x - self.prev_x) * self.lerp_t
            current_y = self.prev_y + (self.grid_y - self.prev_y) * self.lerp_t
            
            # Convert to screen coordinates
            screen_x = int(current_x * 30 - (self.size - 30) // 2)
            screen_y = int(current_y * 30 - (self.size - 30) // 2)
            
            # Update trail with interpolated position
            self.trail.update(screen_x, screen_y)
            
            if self.lerp_t >= 1.0:
                self.moving = False

    def draw(self, surface):
        if not self.has_image:
            return
        
        # Draw trail
        if self.moving or self.lerp_t < 1.0:
            self.trail.draw(surface, self.image)
        
        # Draw current position
        current_x = self.prev_x + (self.grid_x - self.prev_x) * self.lerp_t
        current_y = self.prev_y + (self.grid_y - self.prev_y) * self.lerp_t
        screen_x = int(current_x * 30 - (self.size - 30) // 2)
        screen_y = int(current_y * 30 - (self.size - 30) // 2)
        surface.blit(self.image, (screen_x, screen_y)) 