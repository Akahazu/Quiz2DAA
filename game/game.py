# game.py
import pygame
import sys
from game.settings import *
from game.game_map import Map, wall_diningroom
from game.core import Player
from game.enemies import Enemies


class Game:
    def __init__(self, seed=42, algo1="a_star", algo2="dijkstra"):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"DAA Final Demo – {algo1} vs {algo2} (seed={seed})")
        self.clock = pygame.time.Clock()
        self.running = True

        # Generate map with random costs using the seed
        self.map = Map.from_seed(wall_diningroom, seed)

        # Create player at center
        spawn_x = GRID_WIDTH // 2
        spawn_y = GRID_HEIGHT // 2
        self.player = Player(self.map, spawn_x, spawn_y)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Create enemies with chosen algorithms
        self.enemy1 = Enemies(self.map, self.player, 4, 5, ENEMY_SPEED, algo1, RED)
        self.enemy2 = Enemies(self.map, self.player, 21, 4, ENEMY_SPEED, algo2, ORANGE)
        self.enemies = pygame.sprite.Group(self.enemy1, self.enemy2)
        self.all_sprites.add(self.enemies)

        # Font for cost numbers
        self.cost_font = pygame.font.SysFont("Arial", COST_FONT_SIZE, bold=True)

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_map()
        # Draw path lines
        self.enemy1.draw_path(self.screen)
        self.enemy2.draw_path(self.screen)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def draw_map(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
                if self.map.is_wall(x, y):
                    color = BLACK
                    pygame.draw.rect(self.screen, color, rect)
                else:
                    cost = self.map.get_cost(x, y)
                    # Color based on cost: gradient from light to dark
                    intensity = 200 - (cost - 1) * 25  # cost 1->200, 5->100
                    color = (intensity, intensity, intensity)
                    pygame.draw.rect(self.screen, color, rect)
                    # Draw cost number
                    text = self.cost_font.render(str(cost), True, (0, 0, 0))
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
                # Grid lines
                pygame.draw.rect(self.screen, BLACK, rect, 1)


if __name__ == "__main__":
    # Parse command line: python -m game.game [seed] [algo1] [algo2]
    args = sys.argv[1:]
    seed = int(args[0]) if len(args) > 0 else 42
    algo1 = args[1] if len(args) > 1 else "a_star"
    algo2 = args[2] if len(args) > 2 else "dijkstra"
    
    # Validate algorithms
    valid_algos = {"bfs", "dijkstra", "a_star"}
    if algo1 not in valid_algos or algo2 not in valid_algos:
        print("Invalid algorithm. Choose from: bfs, dijkstra, a_star")
        sys.exit(1)
    game = Game(seed, algo1, algo2)
    game.run()
