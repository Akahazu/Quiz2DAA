import pygame
from pytmx import load_pygame
from settings import *
from core import Player, Projectile, Enemies, PowerUp
from game_map import map_diningroom

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Restaurant 67")
font_large = pygame.font.Font("assets/font/slkscrb.ttf", 26) # Use a large font for titles
font_medium = pygame.font.Font("assets/font/slkscr.ttf", 24) # Use a medium font for options

clock = pygame.time.Clock()
MAP_OPTIONS = {
    "DINNING ROOM": {
        "tmx_data": "assets/Restaurant.tmx",
        "map_data": map_diningroom,
        "spawn_x": GRID_WIDTH // 2,
        "spawn_y": GRID_HEIGHT // 2
    }
}

CHAR_OPTIONS = {
    "BURGERBOY": {
        "idle": "assets/burger.png",
        "run": "assets/burger_run.png"
    },
    
    "BREADWINNER": {
        "idle": "assets/bread.png",
        "run": "assets/bread_run.png"
    }
}

score = 0

game_state = GameState.START_SCREEN

# Load background image (start_screen.jpeg) with try-except block for error handling
try:
    background_image = pygame.image.load("assets/start_screen.jpeg").convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"Error loading background image: {e}")
    print("Using black screen fallback.")
    background_image = None # Fallback to no image if loading fails

CHAR_KEYS = list(CHAR_OPTIONS.keys())
current_char_index = 0

# --- Menu Display Data ---
selected_character = CHAR_KEYS[current_char_index]

powerup_active_timer = 0
powerup_sprite = pygame.sprite.GroupSingle()

# Helper function to render text
def draw_text(surface, text, font, color, x, y, outline_color=(0, 0, 0), outline_size=1):
    # Render the text surface
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    outline_surface = font.render(text, True, outline_color) # Draw the outline by blitting the outline_color text multiple times

    offsets = [ # Offsets for the outline (1 pixel in all 8 directions)
        (-outline_size, -outline_size), (0, -outline_size), (outline_size, -outline_size),
        (-outline_size, 0), (outline_size, 0),
        (-outline_size, outline_size), (0, outline_size), (outline_size, outline_size)
    ]

    for offset_x, offset_y in offsets:
        outline_rect = outline_surface.get_rect(center=(x + offset_x, y + offset_y))
        surface.blit(outline_surface, outline_rect)

    surface.blit(text_surface, text_rect)   # Draw the main text over the outline

def draw_map(surface, tmx_data):
    for layer in tmx_data.visible_layers:
        if hasattr(layer, "tiles"): # tile layer
            for x, y, tile in layer.tiles():
                surface.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

def draw_coins(surface, game_map):
    for x, y in game_map.coins:
        px = x * TILESIZE
        py = y * TILESIZE
        pygame.draw.circle(surface, (255, 215, 0), (px + TILESIZE // 2, py + TILESIZE // 2), TILESIZE // 4)

def draw_powerup(surface, game_map):
    if game_map.powerup_location is not None:
        x, y = game_map.powerup_location
        px = x * TILESIZE
        py = y * TILESIZE
        pygame.draw.circle(surface, POWERUP_COLOR, (px + TILESIZE // 2, py + TILESIZE // 2), POWERUP_SIZE)

def draw_score(surface, score, font, color, x, y, outline_color=(0, 0, 0), outline_size=1):
    score_text = f"SCORE: {score}"
    draw_text(surface, score_text, font, color, x, y, outline_color, outline_size)

def draw_start_screen():
    center_x = SCREEN_WIDTH // 2
    
    # 1. Draw the background image
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((0, 0, 0)) # Fallback color

    # 2. Draw the text over the background
    draw_text(screen, "RESTAURANT 67", font_large, (255, 255, 255), center_x, SCREEN_HEIGHT // 4)
    # Using white or yellow text over the background for contrast
    draw_text(screen, "PRESS ENTER TO START", font_medium, (255, 255, 0), center_x, SCREEN_HEIGHT * 3 // 4)

def draw_character_select_screen():
    center_x = SCREEN_WIDTH // 2
    
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((0, 0, 0))
    
    draw_text(screen, "CHOOSE YOUR MASCOT", font_large, (255, 255, 255), center_x, SCREEN_HEIGHT // 4)
    draw_text(screen, selected_character, font_medium, (0, 150, 255), center_x, SCREEN_HEIGHT // 2)
    
    if current_char_index > 0:
        draw_text(screen, "<", font_medium, (255, 255, 255), center_x - 150, SCREEN_HEIGHT // 2)
    
    if current_char_index < len(CHAR_KEYS) - 1:
        draw_text(screen, ">", font_medium, (255, 255, 255), center_x + 100, SCREEN_HEIGHT // 2)
    
    draw_text(screen, "PRESS ENTER TO CONTINUE", font_medium, (255, 255, 0), center_x, SCREEN_HEIGHT * 3 // 4)

def draw_game_over_screen():
    center_x = SCREEN_WIDTH // 2
    
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((0, 0, 0))
    
    draw_text(screen, "GAME OVER", font_large, (255, 0, 0), center_x, SCREEN_HEIGHT // 3)
    draw_text(screen, f"FINAL SCORE: {player.score}", font_medium, (255, 255, 255), center_x, SCREEN_HEIGHT // 2 - 30)
    draw_text(screen, "PRESS ENTER TO RETRY", font_medium, (255, 255, 0), center_x, SCREEN_HEIGHT // 2 + 30)
    draw_text(screen, "PRESS ESC FOR MAIN MENU", font_medium, (255, 255, 0), center_x, SCREEN_HEIGHT * 3 // 4)

def handle_character_selection(key):
    global game_state, current_char_index, selected_character
    
    if key == pygame.K_RETURN:
        game_state = GameState.GAMEPLAY
    
    elif key == pygame.K_LEFT:
        if current_char_index > 0:
            current_char_index -= 1
            selected_character = CHAR_KEYS[current_char_index]
            
    elif key == pygame.K_RIGHT:
        if current_char_index < len(CHAR_KEYS) - 1:
            current_char_index += 1
            selected_character = CHAR_KEYS[current_char_index]

# Asset Loading
def load_strip(path, frame_width, frame_height):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []

    sheet_width = sheet.get_width()
    for x in range(0, sheet_width, frame_width):
        frame = sheet.subsurface((x, 0, frame_width, frame_height))
        frames.append(frame)

    return frames


idle_frames = load_strip("assets/burger.png", 32, 32)
run_frames = load_strip("assets/burger_run.png", 32, 32)

animations = {
    "idle": idle_frames,
    "run": run_frames,
}

enemy_frame = load_strip("assets/human_walk.png", 32, 32)
enemy_animations = {
    "alive": enemy_frame
}

# Global variables to store the final settings based on character and difficulty selection
FINAL_ENEMIES_COUNT = 0
FINAL_ENEMY_SPEED = 0.0
FINAL_ENEMY_DROP_DELAY = 0
FINAL_SCORE_MULTIPLIER = 1.0
FINAL_RESPAWN_TIME = 0
GAME_INITIALIZED = False    # Semaphore to control one-time setup

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            
            # Handle selection states
            if game_state == GameState.CHARACTER_SELECT:
                handle_character_selection(event.key)

            elif game_state == GameState.GAMEPLAY and event.key == pygame.K_SPACE:
                player.use_skill()

            elif game_state == GameState.GAME_OVER:
                if event.key == pygame.K_RETURN:
                    # Retry - reset and go back to gameplay
                    game_state = GameState.GAMEPLAY
                    GAME_INITIALIZED = False
                elif event.key == pygame.K_ESCAPE:
                    # Return to main menu
                    game_state = GameState.START_SCREEN
                    GAME_INITIALIZED = False
                    current_char_index = 0
                    selected_character = CHAR_KEYS[current_char_index]

            elif event.key == pygame.K_RETURN:
                if game_state == GameState.START_SCREEN:
                    game_state = GameState.CHARACTER_SELECT
                elif game_state == GameState.CHARACTER_SELECT:
                    game_state = GameState.GAMEPLAY

    # Draw Logic based on Current State
    if game_state == GameState.START_SCREEN:
        draw_start_screen()
    elif game_state == GameState.CHARACTER_SELECT:
        draw_character_select_screen()
    elif game_state == GameState.GAME_OVER:
        draw_game_over_screen()
    elif game_state == GameState.GAMEPLAY:
        # Game initialization block - runs once when entering gameplay state
        if not GAME_INITIALIZED:
            char_paths = CHAR_OPTIONS[selected_character]
            char_idle = load_strip(char_paths["idle"], 32, 32)
            char_run = load_strip(char_paths["run"], 32, 32)
            
            selected_animations = {
                "idle": char_idle,
                "run": char_run,
            }

            # Render map and collision data
            maps = MAP_OPTIONS["DINNING ROOM"] 
            tmx_data = load_pygame(maps["tmx_data"])
            map_data = maps["map_data"]
            
            # Reset map state (clear old coins and powerups)
            map_data.coins = set()
            map_data.powerup_location = None
            
            spawn_x = maps["spawn_x"]
            spawn_y = maps["spawn_y"]
            
            # Create Player with the selected animations
            player = Player(selected_animations, map_data , spawn_x, spawn_y, selected_character)
            player_sprite = pygame.sprite.GroupSingle(player)
            all_sprites = pygame.sprite.Group(player)

            # Get the settings based on the final selection
            settings = DIFFICULTY_OPTIONS["NORMAL"] 
            FINAL_ENEMIES_COUNT = settings["enemies"]
            FINAL_ENEMY_SPEED = settings["speed"]
            FINAL_ENEMY_DROP_DELAY = settings["delay"]
            FINAL_SCORE_MULTIPLIER = settings["score_mult"] # get multiplier
            FINAL_RESPAWN_TIME = settings["respawn_time"] # get respawn time

            player.score_multiplier = FINAL_SCORE_MULTIPLIER
            projectiles_sprite = pygame.sprite.Group() 
            player.projectile_group = projectiles_sprite
            enemies_sprite = pygame.sprite.Group()
            
            # Spawn enemies based on difficulty
            if FINAL_ENEMIES_COUNT >= 1:
                # Enemy 1 - Top Left Corner Spawn
                enemy1 = Enemies(map_data, player, 4, 5, FINAL_ENEMY_SPEED, 1, FINAL_ENEMY_DROP_DELAY, FINAL_RESPAWN_TIME)
                enemies_sprite.add(enemy1)
                all_sprites.add(enemy1)
                
            if FINAL_ENEMIES_COUNT >= 2:
                # Enemy 2 - Top Right Corner Spawn
                enemy2 = Enemies(map_data, player, 21, 4, FINAL_ENEMY_SPEED, 2, FINAL_ENEMY_DROP_DELAY, FINAL_RESPAWN_TIME)
                enemies_sprite.add(enemy2)
                all_sprites.add(enemy2)
                
            if FINAL_ENEMIES_COUNT >= 3:
                enemy3 = Enemies(map_data, player, 1, 16, FINAL_ENEMY_SPEED, 1, FINAL_ENEMY_DROP_DELAY, FINAL_RESPAWN_TIME)
                enemies_sprite.add(enemy3)
                all_sprites.add(enemy3)
                
            GAME_INITIALIZED = True
            # End of one-time initialization block

        enemies_sprites_list = enemies_sprite.sprites()

        if powerup_active_timer > 0:
            powerup_active_timer -= 1
            if powerup_active_timer == 0:
                for enemy in enemies_sprites_list:
                    enemy.is_frozen = False

        if maps["map_data"].powerup_location is not None and not powerup_sprite.has(maps["map_data"].powerup_location):
            x, y = maps["map_data"].powerup_location
            powerup_sprite.empty()
            new_powerup = PowerUp(x, y)
            powerup_sprite.add(new_powerup)
        elif maps["map_data"].powerup_location is None:
            powerup_sprite.empty()
        
        # Core game loop logic
        active_enemies = [e for e in enemies_sprite.sprites() if not e.is_dead]
        hits = pygame.sprite.spritecollide(player, enemies_sprite, False)
        for enemy in hits:
            if not enemy.is_dead: # Ignore already dead enemies
                if player.invincible_timer > 0:
                    # Bread Skill is active: Invincible!
                    enemy.die()
                    player.score += int(200 * player.score_multiplier)
                else:
                    # No skill active: Game Over
                    game_state = GameState.GAME_OVER

        projectile_hits = pygame.sprite.groupcollide(projectiles_sprite, enemies_sprite, True, False)
        for projectile, hit_enemies in projectile_hits.items():
            for enemy in hit_enemies:
                enemy.die() # The enemy disappears and starts its respawn timer

        if player.update():
            maps["map_data"].remove_powerup()
            powerup_active_timer = POWERUP_FREEZE_DURATION

            for enemy in enemies_sprites_list:
                enemy.is_frozen = True

        screen.fill((0, 0, 0))
        draw_map(screen, tmx_data)
        draw_coins(screen, map_data)
        all_sprites.update()
        projectiles_sprite.update() 
        powerup_sprite.update()
        all_sprites.draw(screen)
        projectiles_sprite.draw(screen)
        powerup_sprite.draw(screen)
        draw_score(screen, player.score, font_medium, (255, 255, 255), 70, 15)

    pygame.display.flip()