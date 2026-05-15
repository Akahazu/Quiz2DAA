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
        
        self.image = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
        
        # Example color for the projectile (e.g., a pickle slice or tomato)
        self.image.fill((0, 200, 0)) 
        self.rect = self.image.get_rect(center=start_pos)
        
        self.game_map = game_map
        self.speed = PROJECTILE_SPEED
        
        # Determine movement vector based on player's facing direction
        self.direction_x = direction_x
        self.direction_y = direction_y
        
        # Prevent diagonal movement, prioritize horizontal or vertical
        if direction_x != 0:
            self.direction_y = 0
        elif direction_y != 0:
            self.direction_x = 0
        
        # If player is idle (both 0), default to facing right
        if self.direction_x == 0 and self.direction_y == 0:
            self.direction_x = 1

    def update(self):
        # Move the projectile
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed
        
        # Check screen boundaries
        if (self.rect.left < 0 or self.rect.right > SCREEN_WIDTH or
                self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT):
            self.kill()
            return
            
        # Check wall collision (using the center of the projectile)
        tile_x = self.rect.centerx // TILESIZE
        tile_y = self.rect.centery // TILESIZE
        
        if 0 <= tile_x < GRID_WIDTH and 0 <= tile_y < GRID_HEIGHT:
            if self.game_map.is_wall(tile_x, tile_y):
                self.kill() # Projectile hits a wall and disappears

class Player(pygame.sprite.Sprite):
    def __init__(self, animations, map_data, spawn_x, spawn_y, char_type="BURGER BOY"):
        super().__init__()
        self.char_type = char_type
        self.animations = animations
        self.map_data = map_data  # Store the map for collision checks
        self.state = "idle"

        self.frame_index = 0
        self.animation_speed = 0.15

        self.image = self.animations[self.state][0]

        self.start_tile_x = spawn_x # Start the player in the center of a grid cell (e.g., cell (10, 10))
        self.start_tile_y = spawn_y

        # Calculate pixel position for the center of the tile
        self.rect = self.image.get_rect(center=(self.start_tile_x * TILESIZE + TILESIZE // 2, self.start_tile_y * TILESIZE + TILESIZE // 2))

        self.speed = 3
        self.moving = False
        self.flip = False

        self.direction = (1, 0) # Default to facing right

        self.score = 0
        self.score_multiplier = 1.0

        self.tile_x = self.rect.centerx // TILESIZE
        self.tile_y = self.rect.centery // TILESIZE

        self.projectile_group = None

        self.last_tiles = [(self.tile_x, self.tile_y) for _ in range(8)]
        self.invincible_timer = 0

    def update(self):
        # TODO 13: Handle input for movement and call animate()
        pass