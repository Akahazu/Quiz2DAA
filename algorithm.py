from collections import deque
import heapq
from settings import *
from game_map import *

GRID_W = GRID_WIDTH
GRID_H = GRID_HEIGHT

# Helpers
def is_valid(x, y):
    return 0 <= x < GRID_W and 0 <= y < GRID_H


def is_unblocked(grid, x, y):
    return not grid.is_wall(x, y)


def is_destination(x, y, dest):
    return x == dest[0] and y == dest[1]

# ---------- BFS ----------
def bfs_search(grid, src, dest):
    sx, sy = src
    dx, dy = dest

    if not is_valid(sx, sy) or not is_valid(dx, dy):
        return []
    if not is_unblocked(grid, sx, sy) or not is_unblocked(grid, dx, dy):
        return []
    if is_destination(sx, sy, dest):
        return []

    # TODO 4: Initialize visited matrix, parent matrix, and queue for BFS
    
    # TODO 5: Implement the while loop to process the queue and build the path
    
    return []