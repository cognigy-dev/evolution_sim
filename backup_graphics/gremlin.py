import pygame
import math

# Colors
BLACK = (0, 0, 0)       # Base color
BROWN = (139, 69, 19)   # Main body color
DARK_BROWN = (86, 46, 11)  # Shading
YELLOW = (255, 140, 0)  # Orange-yellow for eyes
RED = (255, 50, 50)     # For tongue and pupils
WHITE = (255, 255, 255) # For teeth

class Gremlin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40  # Increased from 30 to 40
        self.tentacle_time = 0  # For tentacle animation
        
    def draw(self, surface):
        # Draw head (main body) - made bigger
        pygame.draw.ellipse(surface, BROWN, 
                          (self.x - 16, self.y - 12,
                           32, 28))
        
        # Draw large ears - made bigger
        pygame.draw.polygon(surface, BROWN, [
            (self.x - 16, self.y),      # Left ear base
            (self.x - 26, self.y - 12),  # Left ear tip
            (self.x - 16, self.y - 12)   # Left ear top
        ])
        pygame.draw.polygon(surface, BROWN, [
            (self.x + 16, self.y),      # Right ear base
            (self.x + 26, self.y - 12),  # Right ear tip
            (self.x + 16, self.y - 12)   # Right ear top
        ])
        
        # Add some shading to ears
        pygame.draw.line(surface, DARK_BROWN,
                        (self.x - 20, self.y - 8),
                        (self.x - 24, self.y - 10), 2)
        pygame.draw.line(surface, DARK_BROWN,
                        (self.x + 20, self.y - 8),
                        (self.x + 24, self.y - 10), 2)
        
        # Draw eyes (yellow circles with red pupils) - slightly bigger
        eye_spacing = 8
        # Left eye
        pygame.draw.circle(surface, YELLOW,
                         (self.x - eye_spacing, self.y - 2), 5)
        pygame.draw.circle(surface, RED,
                         (self.x - eye_spacing, self.y - 2), 2)
        # Right eye
        pygame.draw.circle(surface, YELLOW,
                         (self.x + eye_spacing, self.y - 2), 5)
        pygame.draw.circle(surface, RED,
                         (self.x + eye_spacing, self.y - 2), 2)
        
        # Draw mouth with teeth - wider
        pygame.draw.arc(surface, BLACK,
                       (self.x - 14, self.y - 4, 28, 16),
                       0, math.pi, 2)
        
        # Draw teeth on both sides - bigger
        pygame.draw.rect(surface, WHITE,
                        (self.x - 10, self.y + 4, 4, 4))  # Left tooth
        pygame.draw.rect(surface, WHITE,
                        (self.x + 6, self.y + 4, 4, 4))  # Right tooth
        
        # Draw tongue - bigger
        pygame.draw.polygon(surface, RED, [
            (self.x - 3, self.y + 6),    # Left base
            (self.x + 3, self.y + 6),    # Right base
            (self.x, self.y + 14)        # Tip
        ])
        
        # Add tentacles below the body
        num_tentacles = 4
        tentacle_length = 15
        tentacle_segments = 3
        
        for i in range(num_tentacles):
            start_x = self.x - 15 + (i * 10)
            start_y = self.y + 8
            
            # Create a wavy tentacle effect
            for j in range(tentacle_segments):
                offset = math.sin(self.tentacle_time + i + j) * 3
                end_x = start_x + offset
                end_y = start_y + 5
                
                pygame.draw.line(surface, BROWN, 
                               (start_x, start_y),
                               (end_x, end_y), 2)
                
                start_x = end_x
                start_y = end_y
        
        # Update tentacle animation
        self.tentacle_time += 0.1 