import pygame
import math

class Trail:
    def __init__(self, length=5):
        self.positions = []  # List of (x, y, alpha) positions
        self.max_length = length
        self.fade_speed = 15  # How quickly the trail fades
        self.min_alpha = 30   # Minimum transparency before removing

    def update(self, x, y):
        # Add new position with full alpha
        self.positions.append([x, y, 255])
        
        # Update existing positions
        for pos in self.positions[:-1]:  # Don't fade the newest position
            pos[2] = max(self.min_alpha, pos[2] - self.fade_speed)
            
        # Remove positions that are too faded
        self.positions = [pos for pos in self.positions if pos[2] > self.min_alpha]
        
        # Limit trail length
        if len(self.positions) > self.max_length:
            self.positions = self.positions[-self.max_length:]

    def draw(self, surface, image):
        # Draw trail from oldest to newest
        for x, y, alpha in self.positions[:-1]:  # Don't draw at current position
            trail_image = image.copy()
            trail_image.set_alpha(int(alpha))
            surface.blit(trail_image, (x, y)) 