import pygame
import random
from settings import *
from algorithm import bfs_search
from enemies import Enemies

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Create a small blue circle surface
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.image.fill((0,0,0,0)) # Transparent background
        
        # Draw the blue circle
        center_x = TILESIZE // 2
        center_y = TILESIZE // 2
        pygame.draw.circle(self.image, POWERUP_COLOR, (center_x, center_y), POWERUP_SIZE)
        
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, direction_x, direction_y, game_map):
        super().__init__()
        # TODO 10: Initialize projectile image, rect, speed, and determine movement vector
        pass

    def update(self):
        # TODO 11: Move projectile and check for collision with screen boundaries and walls
        pass

class Player(pygame.sprite.Sprite):
    def __init__(self, animations, map_data, spawn_x, spawn_y, char_type="BURGER BOY"):
        super().__init__()
        # TODO 12: Initialize player properties (animations, map_data, state, start tile, rect, speed, score)
        pass

    def update(self):
        # TODO 13: Handle input for movement and call animate()
        pass