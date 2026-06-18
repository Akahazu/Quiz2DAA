# core.py
import pygame
from game.settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, map_data, tile_x, tile_y):
        super().__init__()
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHT_BLUE)
        self.rect = self.image.get_rect()
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.rect.x = tile_x * TILESIZE
        self.rect.y = tile_y * TILESIZE
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.speed = PLAYER_SPEED
        self.map_data = map_data

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed

        # Horizontal movement with collision
        self.pos_x += dx
        self.rect.x = int(self.pos_x)
        # Check wall collision
        tile_x = self.rect.centerx // TILESIZE
        tile_y = self.rect.centery // TILESIZE
        if self.map_data.is_wall(tile_x, tile_y):
            self.pos_x -= dx
            self.rect.x = int(self.pos_x)

        # Vertical movement with collision
        self.pos_y += dy
        self.rect.y = int(self.pos_y)
        tile_x = self.rect.centerx // TILESIZE
        tile_y = self.rect.centery // TILESIZE
        if self.map_data.is_wall(tile_x, tile_y):
            self.pos_y -= dy
            self.rect.y = int(self.pos_y)

        # Update tile position for enemies to target
        self.tile_x = self.rect.centerx // TILESIZE
        self.tile_y = self.rect.centery // TILESIZE
        # Clamp to grid
        self.tile_x = max(0, min(GRID_WIDTH - 1, self.tile_x))
        self.tile_y = max(0, min(GRID_HEIGHT - 1, self.tile_y))
