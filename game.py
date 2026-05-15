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

# TODO 19: Implement draw_text helper function with outline logic
def draw_text(surface, text, font, color, x, y, outline_color=(0, 0, 0), outline_size=1):
    pass

# TODO 20: Implement state-specific draw functions (draw_start_screen, draw_character_select_screen)
def draw_start_screen():
    pass

def main():
    # TODO 21: Setup the main game loop, event handling (QUIT, KEYDOWN), and game state logic
    pass

if __name__ == "__main__":
    main()