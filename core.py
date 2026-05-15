import pygame
import random
from settings import *
from algorithm import bfs_search
from enemies import Enemies

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # TODO 9: Create the powerup surface, fill with transparent background, and draw a circle
        pass

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