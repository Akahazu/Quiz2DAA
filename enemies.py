import pygame
import random
from settings import *
from algorithm import bfs_search

class Enemies(pygame.sprite.Sprite):
    def __init__(self, game_map, player, tile_x, tile_y, speed, enemy_id, drop_delay, respawn_delay):
        super().__init__()

        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

        self.game_map = game_map
        self.player = player
        self.enemy_id = enemy_id 

        # Dynamic search algorithm setup
        if self.enemy_id == 1:
            self.algorithm = ENEMY_1_ALGORITHM
        elif self.enemy_id == 2:
            self.algorithm = ENEMY_2_ALGORITHM
        else:
            self.algorithm = SearchAlgorithm.DIJKSTRA_SEARCH

        self.initial_tile_x = tile_x
        self.initial_tile_y = tile_y

        self.tile_x = tile_x
        self.tile_y = tile_y

        self.rect.x = tile_x * TILESIZE
        self.rect.y = tile_y * TILESIZE
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

        self.speed = float(speed)
        self.drop_delay = drop_delay
        self.drop_cd = 0
        self.target_tile = None
        self.score = 0

        self.path = []
        self.calculate_path()

        self.is_frozen = False
        self.original_speed = speed

        self.is_dead = False
        self.respawn_timer = 0
        self.respawn_delay = respawn_delay

    def die(self):  # called whenever the enemy died by player's skill
        if not self.is_dead:
            self.is_dead = True
            self.image.fill((0, 0, 0)) 
            self.rect.x = -1000 
            self.pos_x = float(self.rect.x)
            self.respawn_timer = self.respawn_delay
            self.target_tile = None
            self.path = []

    def respawn(self):
        # TODO 16: Reset enemy attributes to spawn point state
        pass