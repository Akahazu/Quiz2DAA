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
        # The order matters: handle input (with collision) then animate
        self.handle_input() 
        self.animate()

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # Update current tile position based on pixel position
        self.tile_x = self.rect.centerx // TILESIZE
        if self.tile_x >= GRID_WIDTH:
            self.tile_x = GRID_WIDTH - 1
        if self.tile_x < 0:
            self.tile_x = 0

        self.tile_y = self.rect.centery // TILESIZE
        if self.tile_y >= GRID_HEIGHT:
            self.tile_y = GRID_HEIGHT - 1
        if self.tile_y < 0:
            self.tile_y = 0

        if (self.tile_x, self.tile_y) != self.last_tiles:
            self.last_tiles.append((self.tile_x, self.tile_y))
            self.last_tiles.pop(0)
        
        if (self.tile_x, self.tile_y) in self.map_data.coins:
            self.map_data.remove_coin(self.tile_x, self.tile_y)
            self.score += int(100 * self.score_multiplier)
        if self.map_data.powerup_location == (self.tile_x, self.tile_y):
            return True
        else:
            return False
        

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.moving = False
        
        # Store original position in case of collision
        original_x = self.rect.x
        original_y = self.rect.y
        
        current_direction_x = 0
        current_direction_y = 0

        # Horizontal Movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.flip = True
            self.moving = True
            current_direction_x = -1
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.flip = False
            self.moving = True
            current_direction_x = 1

        if self.rect.centerx < 0:
            self.rect.x = - self.rect.width // 2
        if self.rect.centerx > SCREEN_WIDTH:
            self.rect.centerx = SCREEN_WIDTH
        if self.rect.centery < 0:
            self.rect.centery = 0
        if self.rect.centery > SCREEN_HEIGHT:
            self.rect.centery = SCREEN_HEIGHT
            
        # Check for horizontal collision
        current_tile_x = max(0, min(GRID_WIDTH - 1, self.rect.centerx // TILESIZE))
        current_tile_y = max(0, min(GRID_HEIGHT - 1, self.rect.centery // TILESIZE))
        
        if self.map_data.is_wall(current_tile_x, current_tile_y):
            self.rect.x = original_x # Revert horizontal movement
            
        original_y = self.rect.y # Reset original_y because horizontal movement might have been reverted
        
        # Vertical Movement
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
            self.moving = True
            current_direction_y = -1
        elif keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            self.moving = True
            current_direction_y = 1

        # Check for vertical collision (use potentially updated x)
        current_tile_x = max(0, min(GRID_WIDTH - 1, self.rect.centerx // TILESIZE))
        current_tile_y = max(0, min(GRID_HEIGHT - 1, self.rect.centery // TILESIZE))
        
        if self.map_data.is_wall(current_tile_x, current_tile_y):
            self.rect.y = original_y # Revert vertical movement
            current_direction_y = 0 # Reset direction if movement reverted
            
        if current_direction_x != 0 or current_direction_y != 0:
            # We will use the horizontal direction unless only vertical was pressed.
            if current_direction_x != 0:
                self.direction = (current_direction_x, 0)
            elif current_direction_y != 0:
                 self.direction = (0, current_direction_y)

        # Re-check moving state after collision resolution
        if original_x != self.rect.x or original_y != self.rect.y:
            self.moving = True
        else:
            self.moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]

        # If any key was pressed AND the position changed, we are running.
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
             # Only switch to idle if no movement occurred despite key press (i.e., collision)
            if self.rect.x == original_x and self.rect.y == original_y:
                self.state = "idle"
            else:
                self.state = "run"
        else:
            self.state = "idle"

    def use_skill(self):
        if self.char_type == "BURGERBOY":
            if self.score >= SKILL_COST and self.projectile_group is not None:
                self.score -= SKILL_COST
                start_pos = self.rect.center
                direction_x, direction_y = self.direction
                new_projectile = Projectile(start_pos, direction_x, direction_y, self.map_data)
                self.projectile_group.add(new_projectile)
        elif self.char_type == "BREADWINNER":
            if self.score >= BREAD_SKILL_COST:
                self.score -= BREAD_SKILL_COST
                self.invincible_timer = BREAD_INVINCIBILITY_DURATION

    def animate(self):
        frames = self.animations[self.state]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(frames):
            self.frame_index = 0

        image = frames[int(self.frame_index)]

        if self.flip:
            image = pygame.transform.flip(image, True, False)

        self.image = image

        if self.invincible_timer > 0:
            if (self.invincible_timer // 5) % 2 == 0: # Flicker effect
                self.image.set_alpha(150)
        else:
            self.image.set_alpha(255)