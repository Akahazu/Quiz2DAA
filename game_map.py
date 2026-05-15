import pygame
from settings import *

class Map:
     def __init__(self, map_walls = [[0 for i in range(GRID_WIDTH)] for j in range(GRID_HEIGHT)], map_intersections = [[0 for i in range(GRID_WIDTH)] for j in range(GRID_HEIGHT)]):
        self.walls = map_walls
        self.intersections = map_intersections
        self.coins = set()
        self.powerup_location = None

     # TODO 7: Implement add_coin, remove_coin, set_powerup, and remove_powerup logic
     def is_wall(self, cell_x, cell_y):
        pass
        
     def add_coin(self, cell_x, cell_y):
        pass

     def remove_coin(self, cell_x, cell_y):
        pass

# TODO 8: Define the wall_diningroom 2D list layout mapping the walls
wall_diningroom = []