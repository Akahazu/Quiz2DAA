# enemies.py
import pygame
from game.settings import *
from game.algorithm import bfs_search, dijkstra_weighted, a_star_weighted


class Enemies(pygame.sprite.Sprite):
    def __init__(
        self, game_map, player, tile_x, tile_y, speed, algorithm="bfs", color=RED
    ):
        super().__init__()
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.color = color

        self.game_map = game_map
        self.player = player
        self.algorithm = algorithm  # 'bfs', 'dijkstra', or 'a_star'

        self.tile_x = tile_x
        self.tile_y = tile_y
        self.rect.x = tile_x * TILESIZE
        self.rect.y = tile_y * TILESIZE
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.speed = float(speed)

        self.target_tile = None
        self.path = []
        self.calculate_path()

    def calculate_path(self):
        target = (self.player.tile_x, self.player.tile_y)
        if self.algorithm == "bfs":
            self.path = bfs_search(self.game_map, (self.tile_x, self.tile_y), target)
        elif self.algorithm == "dijkstra":
            self.path = dijkstra_weighted(
                self.game_map, (self.tile_x, self.tile_y), target
            )
        elif self.algorithm == "a_star":
            self.path = a_star_weighted(
                self.game_map, (self.tile_x, self.tile_y), target
            )
        else:
            self.path = []
        if self.path and self.path[0] == (self.tile_x, self.tile_y):
            self.path.pop(0)
        self.target_tile = None

    def follow_path(self):
        if not self.path and self.target_tile is None:
            return
        if self.target_tile is None:
            if not self.path:
                return
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

        # Check if we've reached the target tile
        if (
            abs(self.pos_x - target_x) < self.speed
            and abs(self.pos_y - target_y) < self.speed
        ):
            self.pos_x = target_x
            self.pos_y = target_y
            self.tile_x, self.tile_y = self.target_tile
            self.target_tile = None

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

    def is_centered_on_tile(self):
        return self.rect.x % TILESIZE == 0 and self.rect.y % TILESIZE == 0

    def update(self):
        # Recalculate path only when centered on a tile and either at a junction or path exhausted
        if self.is_centered_on_tile() and self.target_tile is None:
            # Optionally check if we are at an intersection or path is empty
            # For simplicity, recalculate every time we finish a tile (or we can check game_map.is_intersection)
            self.calculate_path()
        self.follow_path()

    def draw_path(self, surface):
        """Draw a line along the computed path from the enemy's current position to the player."""
        if not self.path:
            return
        # Convert tile coords to pixel centers
        points = []
        # Start from current position (not necessarily tile center)
        current_center = (self.rect.centerx, self.rect.centery)
        points.append(current_center)
        for tx, ty in self.path:
            points.append(
                (tx * TILESIZE + TILESIZE // 2, ty * TILESIZE + TILESIZE // 2)
            )
        # Also add the player's current tile center (the target)
        points.append((self.player.rect.centerx, self.player.rect.centery))
        if len(points) >= 2:
            pygame.draw.lines(surface, self.color, False, points, 2)
