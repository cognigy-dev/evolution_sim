import pygame
import math

class PerspectiveGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 30  # 30x30 pixel squares
        self.horizon_y = height * 0.3  # Horizon line at 30% from top
        self.vanishing_point = (width // 2, int(self.horizon_y))
        
        # Grid parameters
        self.grid_width = 60  # 60 squares wide
        self.grid_depth = 30  # 30 squares deep
        
        # Calculate grid boundaries
        self.grid_left = -self.grid_width * self.cell_size // 2
        self.grid_right = self.grid_width * self.cell_size // 2
        
    def get_grid_position(self, x, y, z):
        """Convert 3D coordinates to 2D screen position with perspective"""
        # Calculate perspective scale (things get smaller as z increases)
        max_depth = self.grid_depth * self.cell_size
        z_scale = 1 - (z / (max_depth * 1.2))  # Slight extra depth for visibility
        
        # Calculate screen position
        screen_x = self.vanishing_point[0] + (x - self.vanishing_point[0]) * z_scale
        screen_y = self.horizon_y + (y - self.horizon_y) * z_scale
        
        return screen_x, screen_y
    
    def draw(self, surface):
        # Draw sky
        pygame.draw.rect(surface, (150, 200, 255),
                        (0, 0, self.width, self.horizon_y))
        
        # Draw ground base color
        pygame.draw.rect(surface, (100, 150, 100),
                        (0, self.horizon_y, self.width, self.height - self.horizon_y))
        
        # Draw grid squares from back to front
        for z in range(self.grid_depth - 1, -1, -1):  # Draw back to front
            z_pos = z * self.cell_size
            
            for x in range(-self.grid_width//2, self.grid_width//2):
                x_pos = x * self.cell_size
                
                # Calculate corners of the grid square
                corners = [
                    (x_pos, 0, z_pos),  # Top-left
                    (x_pos + self.cell_size, 0, z_pos),  # Top-right
                    (x_pos + self.cell_size, 0, z_pos + self.cell_size),  # Bottom-right
                    (x_pos, 0, z_pos + self.cell_size),  # Bottom-left
                ]
                
                # Convert to screen coordinates
                screen_corners = []
                for corner_x, corner_y, corner_z in corners:
                    screen_x, screen_y = self.get_grid_position(corner_x, 
                                                              self.horizon_y + 300, 
                                                              corner_z)
                    screen_corners.append((int(screen_x), int(screen_y)))
                
                # Draw square with slight transparency
                alpha = max(0, min(255, 255 * (1 - z/self.grid_depth)))
                if (x + z) % 2 == 0:  # Checkerboard pattern
                    color = (90, 140, 90, alpha)  # Slightly darker green
                else:
                    color = (110, 160, 110, alpha)  # Slightly lighter green
                
                # Create surface for the square with alpha
                square_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.polygon(square_surface, color, screen_corners)
                surface.blit(square_surface, (0, 0)) 