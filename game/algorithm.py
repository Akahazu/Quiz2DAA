from collections import deque
import heapq
from game.settings import *
from game.game_map import *

GRID_W = GRID_WIDTH
GRID_H = GRID_HEIGHT

# Helpers
def is_valid(x, y):
    return 0 <= x < GRID_W and 0 <= y < GRID_H


def is_unblocked(grid, x, y):
    return not grid.is_wall(x, y)


def is_destination(x, y, dest):
    return x == dest[0] and y == dest[1]

# BFS Algorithm
def bfs_search(grid, src, dest):
    sx, sy = src
    dx, dy = dest

    if not is_valid(sx, sy) or not is_valid(dx, dy):
        return []

    if not is_unblocked(grid, sx, sy) or not is_unblocked(grid, dx, dy):
        return []

    if is_destination(sx, sy, dest):
        return []

    visited = [[False for _ in range(GRID_W)] for _ in range(GRID_H)]
    parent = [[(-1, -1) for _ in range(GRID_W)] for _ in range(GRID_H)]
    
    visited[sy][sx] = True
    parent[sy][sx] = (sx, sy)
    
    queue = deque([(sx, sy)])
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    while queue:
        x, y = queue.popleft()
        
        for dx_step, dy_step in directions:
            nx = x + dx_step
            ny = y + dy_step
            
            if not is_valid(nx, ny):
                continue
            if visited[ny][nx]:
                continue
            if not is_unblocked(grid, nx, ny):
                continue
            
            visited[ny][nx] = True
            parent[ny][nx] = (x, y)
            
            if is_destination(nx, ny, dest):
                # Trace path
                path = []
                cx, cy = dest
                while parent[cy][cx] != (cx, cy):
                    path.append((cx, cy))
                    cx, cy = parent[cy][cx]
                path.append((cx, cy))
                path.reverse()
                return path
            
            queue.append((nx, ny))
    
    return []

## Dijkstra's Algorithm
def dijkstra_search(grid, src, dest):
    sx, sy = src
    dx, dy = dest

    if not is_valid(sx, sy) or not is_valid(dx, dy):
        return []

    if not is_unblocked(grid, sx, sy) or not is_unblocked(grid, dx, dy):
        return []

    if is_destination(sx, sy, dest):
        return []

    visited = [[False for _ in range(GRID_W)] for _ in range(GRID_H)]
    parent = [[(-1, -1) for _ in range(GRID_W)] for _ in range(GRID_H)]
    distance = [[float('inf') for _ in range(GRID_W)] for _ in range(GRID_H)]
    
    distance[sy][sx] = 0
    parent[sy][sx] = (sx, sy)
    
    heap = [(0, sx, sy)]
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    while heap:
        dist, x, y = heapq.heappop(heap)
        
        if visited[y][x]:
            continue
        visited[y][x] = True
        
        for dx_step, dy_step in directions:
            nx = x + dx_step
            ny = y + dy_step
            
            if not is_valid(nx, ny):
                continue
            if visited[ny][nx]:
                continue
            if not is_unblocked(grid, nx, ny):
                continue
            
            new_dist = dist + 1
            
            if new_dist < distance[ny][nx]:
                distance[ny][nx] = new_dist
                parent[ny][nx] = (x, y)
                heapq.heappush(heap, (new_dist, nx, ny))
                
                if is_destination(nx, ny, dest):
                    # Trace path
                    path = []
                    cx, cy = dest
                    while parent[cy][cx] != (cx, cy):
                        path.append((cx, cy))
                        cx, cy = parent[cy][cx]
                    path.append((cx, cy))
                    path.reverse()
                    return path
    
    return []