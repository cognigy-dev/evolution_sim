import pygame
import os
from datetime import datetime
from config import SQUARE_SIZE

def log_error(message):
    with open("graphics_error.log", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

class Herbivore:
    def __init__(self, x, y):
        print("Initializing Herbivore...")
        self.x = x
        self.y = y
        self.size = 45
        self.direction = 'right'
        self.prev_x = x
        
        # Load the herbivore image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'assets', 'herbivore.png')
        
        print(f"Current working directory: {os.getcwd()}")
        try:
            with open("image_loading.log", "a") as log:
                log.write("\nTesting log file creation")
            print("Successfully created log file")
        except Exception as e:
            print(f"Failed to create log file: {e}")
            
            with open("image_loading.log", "a") as log:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log.write(f"\n[{timestamp}] Attempting to load herbivore image from: {image_path}\n")
                
                try:
                    self.base_image = pygame.image.load(image_path).convert_alpha()
                    self.base_image = pygame.transform.scale(self.base_image, (self.size, self.size))
                    self.image = self.base_image
                    self.has_image = True
                    log.write(f"[{timestamp}] Successfully loaded herbivore image\n")
                except Exception as e:
                    self.has_image = False
                    log.write(f"[{timestamp}] Failed to load herbivore image: {str(e)}\n")

    def update(self):
        if self.x != self.prev_x:
            if self.x > self.prev_x:
                self.direction = 'right'
                self.image = self.base_image
            else:
                self.direction = 'left'
                self.image = pygame.transform.flip(self.base_image, True, False)
            self.prev_x = self.x

    def draw(self, surface):
        if self.has_image:
            screen_x = self.x - (self.size - SQUARE_SIZE) // 2
            screen_y = self.y - (self.size - SQUARE_SIZE) // 2
            surface.blit(self.image, (screen_x, screen_y))
        else:
            log_error(f"Attempted to draw herbivore at ({self.x}, {self.y}) but image was not loaded") 