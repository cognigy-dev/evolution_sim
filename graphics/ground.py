import pygame
import random

class Ground:
    def __init__(self, grid_width, grid_height, square_size):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.square_size = square_size
        
        # Create procedural textures with different brown shades
        self.base_texture = self.create_brown_texture(square_size, (171, 155, 127))  # Light earthy brown
        self.var_texture = self.create_brown_texture(square_size, (162, 142, 111))   # Slightly darker brown
        
        # Create a cached surface for better performance
        self.surface = pygame.Surface((grid_width * square_size, grid_height * square_size))
        self.render_ground()

    def create_brown_texture(self, size, base_color):
        """Create a natural-looking brown texture"""
        surface = pygame.Surface((size, size))
        
        # Base brown color
        surface.fill(base_color)
        
        # Add subtle variations
        for _ in range(size * 2):
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            # Random slight variation of base color
            shade = random.randint(-15, 15)
            variation = (
                max(0, min(255, base_color[0] + shade)),
                max(0, min(255, base_color[1] + shade)),
                max(0, min(255, base_color[2] + shade))
            )
            pygame.draw.circle(surface, variation, (x, y), random.randint(1, 2))
        
        return surface

    def render_ground(self):
        """Pre-render the ground texture"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                pos = (x * self.square_size, y * self.square_size)
                # Alternate between base and variant textures for subtle pattern
                texture = self.base_texture if (x + y) % 2 == 0 else self.var_texture
                self.surface.blit(texture, pos)

    def draw(self, surface):
        """Draw the pre-rendered ground"""
        surface.blit(self.surface, (0, 0)) 