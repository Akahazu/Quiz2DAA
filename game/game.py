import pygame
import logging
from typing import List, Tuple, Optional
from pathlib import Path
from pytmx import load_pygame, TiledMap
from game.settings import *
from game.core import Player, PowerUp
from game.enemies import Enemies
from game.game_map import map_diningroom

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("game.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Restaurant67")

ASSETS_DIR = Path("assets")
FONT_DIR = ASSETS_DIR / "font"
BACKGROUND_PATH = ASSETS_DIR / "start_screen.jpeg"
MAP_OPTIONS = {
    "DINNING ROOM": {
        "tmx_data": ASSETS_DIR / "Restaurant.tmx",
        "map_data": map_diningroom,
        "spawn_x": GRID_WIDTH // 2,
        "spawn_y": GRID_HEIGHT // 2
    }
}
CHAR_OPTIONS = {
    "BURGERBOY": {"idle": ASSETS_DIR / "burger.png", "run": ASSETS_DIR / "burger_run.png"},
    "BREADWINNER": {"idle": ASSETS_DIR / "bread.png", "run": ASSETS_DIR / "bread_run.png"}
}

def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    x: int,
    y: int,
    outline_color: Tuple[int, int, int] = (0, 0, 0),
    outline_size: int = 1
) -> None:
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    outline_surface = font.render(text, True, outline_color)
    offsets = [
        (-outline_size, -outline_size), (0, -outline_size), (outline_size, -outline_size),
        (-outline_size, 0), (outline_size, 0),
        (-outline_size, outline_size), (0, outline_size), (outline_size, outline_size)
    ]
    for dx, dy in offsets:
        outline_rect = outline_surface.get_rect(center=(x + dx, y + dy))
        surface.blit(outline_surface, outline_rect)
    surface.blit(text_surface, text_rect)

def load_strip(path: Path, frame_width: int, frame_height: int) -> List[pygame.Surface]:
    if not path.exists():
        raise FileNotFoundError(f"Sprite sheet not found: {path}")
    sheet = pygame.image.load(str(path)).convert_alpha()
    frames: List[pygame.Surface] = []
    sheet_width = sheet.get_width()
    for x in range(0, sheet_width, frame_width):
        frame = sheet.subsurface((x, 0, frame_width, frame_height))
        frames.append(frame)
    return frames

# --- Asset Loader (Single Responsibility) ---
class AssetLoader:
    def __init__(self) -> None:
        self.font_large: Optional[pygame.font.Font] = None
        self.font_medium: Optional[pygame.font.Font] = None
        self.background: Optional[pygame.Surface] = None
        self._load_assets()

    def _load_assets(self) -> None:
        try:
            self.font_large = pygame.font.Font(str(FONT_DIR / "slkscrb.ttf"), 26)
            self.font_medium = pygame.font.Font(str(FONT_DIR / "slkscr.ttf"), 24)
            logger.info("Fonts loaded successfully.")
        except FileNotFoundError as e:
            logger.error(f"Font file missing: {e}")
            # Fallback to default font
            self.font_large = pygame.font.Font(None, 26)
            self.font_medium = pygame.font.Font(None, 24)

        try:
            self.background = pygame.image.load(str(BACKGROUND_PATH)).convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            logger.info("Background image loaded.")
        except pygame.error as e:
            logger.error(f"Failed to load background: {e}")
            self.background = None  # will be handled by draw methods

    def get_font(self, size: str) -> pygame.font.Font:
        """Return the requested font, raising if not loaded."""
        if size == "large":
            if self.font_large is None:
                raise RuntimeError("Large font not loaded")
            return self.font_large
        elif size == "medium":
            if self.font_medium is None:
                raise RuntimeError("Medium font not loaded")
            return self.font_medium
        else:
            raise ValueError("Invalid font size requested")

    def get_background(self) -> Optional[pygame.Surface]:
        return self.background

# --- Map Manager (handles TMX and game map data) ---
class MapManager:
    def __init__(self, map_key: str) -> None:
        self.map_key = map_key
        self.config = MAP_OPTIONS[map_key]
        self.tmx_data: Optional[TiledMap] = None
        self.map_data = self.config["map_data"]  # assumed to have coins, powerup_location, remove_powerup
        self.spawn_x = self.config["spawn_x"]
        self.spawn_y = self.config["spawn_y"]
        self._load_tmx()

    def _load_tmx(self) -> None:
        try:
            self.tmx_data = load_pygame(str(self.config["tmx_data"]))
            logger.info(f"TMX map loaded: {self.config['tmx_data']}")
        except Exception as e:
            logger.error(f"Failed to load TMX map: {e}")
            raise

    def get_tmx(self) -> TiledMap:
        if self.tmx_data is None:
            raise RuntimeError("TMX data not loaded")
        return self.tmx_data

    def reset_map_state(self) -> None:
        """Clear coins and powerups for a fresh start."""
        self.map_data.coins = set()
        self.map_data.powerup_location = None

    def draw_map(self, surface: pygame.Surface) -> None:
        tmx = self.get_tmx()
        for layer in tmx.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles():
                    surface.blit(tile, (x * tmx.tilewidth, y * tmx.tileheight))

    def draw_coins(self, surface: pygame.Surface) -> None:
        for x, y in self.map_data.coins:
            px = x * TILESIZE
            py = y * TILESIZE
            pygame.draw.circle(surface, (255, 215, 0), (px + TILESIZE // 2, py + TILESIZE // 2), TILESIZE // 4)

    def draw_powerup(self, surface: pygame.Surface) -> None:
        if self.map_data.powerup_location is not None:
            x, y = self.map_data.powerup_location
            px = x * TILESIZE
            py = y * TILESIZE
            pygame.draw.circle(surface, POWERUP_COLOR, (px + TILESIZE // 2, py + TILESIZE // 2), POWERUP_SIZE)

# --- Game Class (main controller, follows Single Responsibility for orchestration) ---
class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Restaurant 67")
        self.clock = pygame.time.Clock()
        self.running = True

        self.asset_loader = AssetLoader()
        self.font_large = self.asset_loader.get_font("large")
        self.font_medium = self.asset_loader.get_font("medium")
        self.background = self.asset_loader.get_background()

        self.state = GameState.START_SCREEN
        self.char_keys = list(CHAR_OPTIONS.keys())
        self.current_char_index = 0
        self.selected_character = self.char_keys[self.current_char_index]

        # Gameplay state (initialised when entering GAMEPLAY)
        self.player: Optional[Player] = None
        self.player_sprite: Optional[pygame.sprite.GroupSingle] = None
        self.all_sprites: Optional[pygame.sprite.Group] = None
        self.enemies_sprite: Optional[pygame.sprite.Group] = None
        self.projectiles_sprite: Optional[pygame.sprite.Group] = None
        self.powerup_sprite = pygame.sprite.GroupSingle()
        self.powerup_active_timer = 0
        self.map_manager: Optional[MapManager] = None
        self.game_initialized = False

        # Difficulty settings (default)
        self.difficulty = "NORMAL"
        self._apply_difficulty()

        logger.info("Game initialized")

    def _apply_difficulty(self) -> None:
        settings = DIFFICULTY_OPTIONS[self.difficulty]
        self.enemies_count = settings["enemies"]
        self.enemy_speed = settings["speed"]
        self.enemy_drop_delay = settings["delay"]
        self.score_multiplier = settings["score_mult"]
        self.respawn_time = settings["respawn_time"]

    def _initialize_gameplay(self) -> None:
        """Create all game objects for a new play session."""
        logger.info("Initializing gameplay...")
        self.map_manager = MapManager("DINNING ROOM")
        self.map_manager.reset_map_state()
        tmx = self.map_manager.get_tmx()

        # Load character animations
        char_paths = CHAR_OPTIONS[self.selected_character]
        idle_frames = load_strip(char_paths["idle"], 32, 32)
        run_frames = load_strip(char_paths["run"], 32, 32)
        animations = {"idle": idle_frames, "run": run_frames}

        # Create player
        spawn_x = self.map_manager.spawn_x
        spawn_y = self.map_manager.spawn_y
        self.player = Player(animations, self.map_manager.map_data, spawn_x, spawn_y, self.selected_character)
        self.player.score_multiplier = self.score_multiplier
        self.player_sprite = pygame.sprite.GroupSingle(self.player)
        self.all_sprites = pygame.sprite.Group(self.player)

        self.projectiles_sprite = pygame.sprite.Group()
        self.player.projectile_group = self.projectiles_sprite

        self.enemies_sprite = pygame.sprite.Group()
        self._spawn_enemies()

        self.powerup_sprite.empty()
        self.powerup_active_timer = 0
        self.game_initialized = True
        logger.info("Gameplay initialized.")

    def _spawn_enemies(self) -> None:
        """Spawn enemies according to difficulty."""
        if self.enemies_count >= 1:
            enemy1 = Enemies(
                self.map_manager.map_data, self.player, 4, 5,
                self.enemy_speed, 1, self.enemy_drop_delay, self.respawn_time
            )
            self.enemies_sprite.add(enemy1)
            self.all_sprites.add(enemy1)
        if self.enemies_count >= 2:
            enemy2 = Enemies(
                self.map_manager.map_data, self.player, 21, 4,
                self.enemy_speed, 2, self.enemy_drop_delay, self.respawn_time
            )
            self.enemies_sprite.add(enemy2)
            self.all_sprites.add(enemy2)
        if self.enemies_count >= 3:
            enemy3 = Enemies(
                self.map_manager.map_data, self.player, 1, 16,
                self.enemy_speed, 1, self.enemy_drop_delay, self.respawn_time
            )
            self.enemies_sprite.add(enemy3)
            self.all_sprites.add(enemy3)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key: int) -> None:
        if self.state == GameState.START_SCREEN:
            if key == pygame.K_RETURN:
                self.state = GameState.CHARACTER_SELECT
                logger.info("Transitioned to CHARACTER_SELECT")
        elif self.state == GameState.CHARACTER_SELECT:
            if key == pygame.K_RETURN:
                self.state = GameState.GAMEPLAY
                self.game_initialized = False  # force re-init
                logger.info("Transitioned to GAMEPLAY")
            elif key == pygame.K_LEFT:
                if self.current_char_index > 0:
                    self.current_char_index -= 1
                    self.selected_character = self.char_keys[self.current_char_index]
            elif key == pygame.K_RIGHT:
                if self.current_char_index < len(self.char_keys) - 1:
                    self.current_char_index += 1
                    self.selected_character = self.char_keys[self.current_char_index]
        elif self.state == GameState.GAMEPLAY:
            if key == pygame.K_SPACE and self.player is not None:
                self.player.use_skill()
        elif self.state == GameState.GAME_OVER:
            if key == pygame.K_RETURN:
                self.state = GameState.GAMEPLAY
                self.game_initialized = False
                logger.info("Retry - restarting gameplay")
            elif key == pygame.K_ESCAPE:
                self.state = GameState.START_SCREEN
                self.game_initialized = False
                self.current_char_index = 0
                self.selected_character = self.char_keys[self.current_char_index]
                logger.info("Returned to main menu")

    def update(self) -> None:
        if self.state == GameState.GAMEPLAY:
            if not self.game_initialized:
                self._initialize_gameplay()

            if self.player is None or self.enemies_sprite is None or self.all_sprites is None:
                logger.error("Gameplay objects missing, cannot update")
                self.state = GameState.GAME_OVER
                return

            # Powerup timer
            if self.powerup_active_timer > 0:
                self.powerup_active_timer -= 1
                if self.powerup_active_timer == 0:
                    for enemy in self.enemies_sprite.sprites():
                        if hasattr(enemy, 'is_frozen'):
                            enemy.is_frozen = False

            # Powerup spawning
            map_data = self.map_manager.map_data

            if map_data.powerup_location is not None and not self.powerup_sprite:
                x, y = map_data.powerup_location
                new_powerup = PowerUp(x, y)
                self.powerup_sprite.add(new_powerup)
            elif map_data.powerup_location is None:
                self.powerup_sprite.empty()

            # Collision: player vs enemies
            hits = pygame.sprite.spritecollide(self.player, self.enemies_sprite, False)
            for enemy in hits:
                if hasattr(enemy, 'is_dead') and not enemy.is_dead:
                    if self.player.invincible_timer > 0:
                        enemy.die()
                        self.player.score += int(200 * self.player.score_multiplier)
                    else:
                        logger.info("Player hit by enemy - GAME OVER")
                        self.state = GameState.GAME_OVER
                        return

            # Collision: projectiles vs enemies
            if self.projectiles_sprite is not None:
                projectile_hits = pygame.sprite.groupcollide(self.projectiles_sprite, self.enemies_sprite, True, False)
                for _, hit_enemies in projectile_hits.items():
                    for enemy in hit_enemies:
                        if hasattr(enemy, 'die'):
                            enemy.die()

            # Player update (may trigger powerup collection)
            if self.player.player_update():
                self.map_manager.map_data.remove_powerup()
                self.powerup_active_timer = POWERUP_FREEZE_DURATION
                for enemy in self.enemies_sprite.sprites():
                    if hasattr(enemy, 'is_frozen'):
                        enemy.is_frozen = True

            # Update all sprite groups
            self.all_sprites.update()
            if self.projectiles_sprite is not None:
                self.projectiles_sprite.update()
            self.powerup_sprite.update()

    def draw(self) -> None:
        if self.state == GameState.START_SCREEN:
            self._draw_start_screen()
        elif self.state == GameState.CHARACTER_SELECT:
            self._draw_character_select()
        elif self.state == GameState.GAMEPLAY:
            self._draw_gameplay()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_start_screen(self) -> None:
        self.screen.fill((0, 0, 0))
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        center_x = SCREEN_WIDTH // 2
        draw_text(self.screen, "RESTAURANT 67", self.font_large, (255, 255, 255),
                  center_x, SCREEN_HEIGHT // 4)
        draw_text(self.screen, "PRESS ENTER TO START", self.font_medium, (255, 255, 0),
                  center_x, SCREEN_HEIGHT * 3 // 4)

    def _draw_character_select(self) -> None:
        self.screen.fill((0, 0, 0))
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        center_x = SCREEN_WIDTH // 2
        draw_text(self.screen, "CHOOSE YOUR MASCOT", self.font_large, (255, 255, 255),
                  center_x, SCREEN_HEIGHT // 4)
        draw_text(self.screen, self.selected_character, self.font_medium, (0, 150, 255),
                  center_x, SCREEN_HEIGHT // 2)
        if self.current_char_index > 0:
            draw_text(self.screen, "<", self.font_medium, (255, 255, 255),
                      center_x - 150, SCREEN_HEIGHT // 2)
        if self.current_char_index < len(self.char_keys) - 1:
            draw_text(self.screen, ">", self.font_medium, (255, 255, 255),
                      center_x + 100, SCREEN_HEIGHT // 2)
        draw_text(self.screen, "PRESS ENTER TO CONTINUE", self.font_medium, (255, 255, 0),
                  center_x, SCREEN_HEIGHT * 3 // 4)

    def _draw_gameplay(self) -> None:
        if self.map_manager is None or self.all_sprites is None:
            logger.error("Cannot draw gameplay - map or sprites missing")
            return

        self.screen.fill((0, 0, 0))
        self.map_manager.draw_map(self.screen)
        self.map_manager.draw_coins(self.screen)
        self.all_sprites.draw(self.screen)
        if self.projectiles_sprite is not None:
            self.projectiles_sprite.draw(self.screen)
        self.powerup_sprite.draw(self.screen)
        # Draw score
        if self.player is not None:
            draw_text(self.screen, f"SCORE: {self.player.score}", self.font_medium,
                      (255, 255, 255), 70, 15)

    def _draw_game_over(self) -> None:
        self.screen.fill((0, 0, 0))
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        center_x = SCREEN_WIDTH // 2
        draw_text(self.screen, "GAME OVER", self.font_large, (255, 0, 0),
                  center_x, SCREEN_HEIGHT // 3)
        final_score = self.player.score if self.player is not None else 0
        draw_text(self.screen, f"FINAL SCORE: {final_score}", self.font_medium,
                  (255, 255, 255), center_x, SCREEN_HEIGHT // 2 - 30)
        draw_text(self.screen, "PRESS ENTER TO RETRY", self.font_medium, (255, 255, 0),
                  center_x, SCREEN_HEIGHT // 2 + 30)
        draw_text(self.screen, "PRESS ESC FOR MAIN MENU", self.font_medium, (255, 255, 0),
                  center_x, SCREEN_HEIGHT * 3 // 4)

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        logger.info("Game exited.")

# --- Entry Point ---
if __name__ == "__main__":
    game = Game()
    game.run()
