import pygame
from settings import *
from core import Player, Projectile, Enemies, PowerUp
from game_map import Map 

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

def main():
    # TODO 21: Setup the main game loop, event handling (QUIT, KEYDOWN), and game state logic
    pass

if __name__ == "__main__":
    main()