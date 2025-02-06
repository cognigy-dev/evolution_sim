import pygame
import os
from datetime import datetime

def log_error(message):
    with open("graphics_error.log", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

class Omnivore:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30  # Match CELL_SIZE
        self.direction = 'right'
        
        # Load the omnivore image from graphics/assets
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'assets', 'omnivore.png')
        log_error(f"Trying to load omnivore image from: {os.path.abspath(image_path)}")
        
        try:
            self.base_image = pygame.image.load(image_path).convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (self.size, self.size))
            self.image = self.base_image
            self.has_image = True
            log_error("Successfully loaded omnivore image")
        except Exception as e:
            log_error(f"Error loading omnivore image from {image_path}: {e}")
            self.has_image = False
    
    def draw(self, surface):
        if self.has_image:
            surface.blit(self.image, (self.x, self.y))
        else:
            log_error(f"Attempted to draw omnivore at ({self.x}, {self.y}) but image was not loaded") 