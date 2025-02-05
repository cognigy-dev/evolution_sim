import pygame
import math
import os

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
        self.size = 60
        self.sway_time = 0
        self.age = 0  # Add age counter
        
        # Load the gremlin image - using absolute path from script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'assets', 'omnivore.png')
        
        try:
            self.base_image = pygame.image.load(image_path).convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (self.size, self.size))
            self.has_image = True
            # Create tinted versions for different ages
            self.update_age_appearance()
        except Exception as e:
            print(f"Error loading omnivore image from {image_path}: {e}")
            self.has_image = False
    
    def update_age_appearance(self):
        if not self.has_image:
            return
            
        # Create a copy of the base image
        self.image = self.base_image.copy()
        
        # Apply color tint based on age
        if self.age > 1000:  # Elder
            self.apply_tint((150, 150, 180))  # Grayish blue tint
        elif self.age > 500:  # Adult
            self.apply_tint((100, 100, 150))  # Slight blue tint
        elif self.age > 200:  # Young adult
            self.apply_tint((50, 50, 100))  # Very slight blue tint
        # Young gremlin keeps original color
    
    def apply_tint(self, tint_color):
        # Create a surface for tinting
        tint_surface = pygame.Surface(self.image.get_size()).convert_alpha()
        tint_surface.fill(tint_color)
        # Apply tint while preserving transparency
        self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    def update(self):
        self.age += 1
        if self.age % 100 == 0:  # Check for age milestones
            self.update_age_appearance()
    
    def draw(self, surface):
        # Calculate hover effect
        hover = math.sin(self.sway_time) * 3
        
        if self.has_image:
            # Draw the image centered at x,y with hover effect
            surface.blit(self.image, 
                        (self.x - self.size//2,
                         self.y - self.size//2 + hover))
        else:
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
                    offset = math.sin(self.sway_time + i + j) * 3
                    end_x = start_x + offset
                    end_y = start_y + 5
                    
                    pygame.draw.line(surface, BROWN, 
                                   (start_x, start_y),
                                   (end_x, end_y), 2)
                    
                    start_x = end_x
                    start_y = end_y
        
        self.sway_time += 0.1 