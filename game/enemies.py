import pygame
import random
from game.settings import *
from game.algorithm import bfs_search, dijkstra_search

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

    def die(self):      # Called whenever the enemy died by player's skill
        if not self.is_dead:
            self.is_dead = True
            self.image.fill((0, 0, 0)) 
            self.rect.x = -1000 
            self.pos_x = float(self.rect.x)
            self.respawn_timer = self.respawn_delay
            self.target_tile = None
            self.path = []

    def respawn(self):  # Resets enemy to initial spawn point and state
        self.is_dead = False
        self.image.fill((255, 0, 0))
        self.tile_x = self.initial_tile_x
        self.tile_y = self.initial_tile_y
        self.rect.x = self.tile_x * TILESIZE
        self.rect.y = self.tile_y * TILESIZE
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.target_tile = None
        self.calculate_path()

    def calculate_path(self):
        # Enemy targets player's current position, but Enemy 2 targets player's position from 7 frames ago for a conering effect
        target = (self.player.tile_x, self.player.tile_y)
        if self.enemy_id == 2:
            target = self.player.last_tiles[7]

        if self.algorithm == SearchAlgorithm.DIJKSTRA_SEARCH:
            self.path = dijkstra_search(
                self.game_map,
                (self.tile_x, self.tile_y),
                target
            )
        elif self.algorithm == SearchAlgorithm.BFS_SEARCH:
            self.path = bfs_search(
                self.game_map,
                (self.tile_x, self.tile_y),
                target
            )

        if self.path and self.path[0] == (self.tile_x, self.tile_y):
            self.path.pop(0)

    def follow_path(self):
        if self.is_frozen:
            return

        if not self.path and self.target_tile is None:
            return

        if self.target_tile is None:
            self.target_tile = self.path.pop(0)

        target_x = self.target_tile[0] * TILESIZE
        target_y = self.target_tile[1] * TILESIZE

        if self.pos_x < target_x:
            self.pos_x += self.speed
        elif self.pos_x > target_x:
            self.pos_x -= self.speed
        elif self.pos_y < target_y:
            self.pos_y += self.speed
        elif self.pos_y > target_y:
            self.pos_y -= self.speed

        if abs(self.pos_x - target_x) < self.speed and abs(self.pos_y - target_y) < self.speed:
            self.pos_x = target_x
            self.pos_y = target_y

            self.tile_x, self.tile_y = self.target_tile
            self.target_tile = None

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

    def is_centered_on_tile(self):
        return (
            self.rect.x % TILESIZE == 0 and
            self.rect.y % TILESIZE == 0
        )
    
    def spawn_coin(self):
        self.game_map.add_coin(self.tile_x, self.tile_y)

    def update(self):
        if self.is_dead:
            if self.respawn_timer > 0:
                self.respawn_timer -= 1
            else:
                self.respawn()
            return

        if self.is_frozen:
            self.image.fill((100, 100, 100))
        else:
            self.image.fill((255, 0, 0))
            if self.is_centered_on_tile() and self.target_tile is None:
                if self.game_map.is_intersection(self.tile_x, self.tile_y) or not self.path:
                    self.calculate_path()

            if self.is_centered_on_tile():
                if (self.drop_cd > 0):
                    self.drop_cd -= 1
                elif (self.tile_x, self.tile_y) not in self.game_map.coins:
                    if random.random() < POWERUP_DROP_CHANCE:
                        if self.game_map.powerup_location is None:
                            self.game_map.set_powerup(self.tile_x, self.tile_y)
                    else:
                        self.spawn_coin()
                        self.score += 100
                    self.drop_cd = self.drop_delay

            self.follow_path()