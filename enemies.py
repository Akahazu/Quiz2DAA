import pygame
import random
from settings import *
from algorithm import bfs_search

class Enemies(pygame.sprite.Sprite):
    def __init__(self, game_map, player, tile_x, tile_y, speed, enemy_id, drop_delay, respawn_delay):
        super().__init__()
        # TODO 14: Initialize enemy attributes and setup algorithm dynamically based on enemy_id
        pass

    def die(self):
        # TODO 15: Implement logic when enemy dies (set state, move rect off-screen, start respawn timer)
        pass

    def respawn(self):
        # TODO 16: Reset enemy attributes to spawn point state
        pass