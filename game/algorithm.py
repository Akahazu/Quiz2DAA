# algorithm.py
from collections import deque
import heapq
from game.settings import *

GRID_W = GRID_WIDTH
GRID_H = GRID_HEIGHT


def is_valid(x, y):
    return 0 <= x < GRID_W and 0 <= y < GRID_H


def is_unblocked(grid, x, y):
    return not grid.is_wall(x, y)


def is_destination(x, y, dest):
    return x == dest[0] and y == dest[1]


# BFS (unweighted)
def bfs_search(grid, src, dest):
    sx, sy = src
    dx, dy = dest
    if not is_valid(sx, sy) or not is_valid(dx, dy):
        return []
    if not is_unblocked(grid, sx, sy) or not is_unblocked(grid, dx, dy):
        return []
    if is_destination(sx, sy, dest):
        return []

    visited = [[False] * GRID_W for _ in range(GRID_H)]
    parent = [[(-1, -1)] * GRID_W for _ in range(GRID_H)]
    visited[sy][sx] = True
    parent[sy][sx] = (sx, sy)
    queue = deque([(sx, sy)])
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        x, y = queue.popleft()
        for dx_step, dy_step in directions:
            nx, ny = x + dx_step, y + dy_step
            if not is_valid(nx, ny):
                continue
            if visited[ny][nx]:
                continue
            if not is_unblocked(grid, nx, ny):
                continue
            visited[ny][nx] = True
            parent[ny][nx] = (x, y)
            if is_destination(nx, ny, dest):
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


# Weighted Dijkstra
def dijkstra_weighted(grid, src, dest):
    sx, sy = src
    dx, dy = dest
    if not is_valid(sx, sy) or not is_valid(dx, dy):
        return []
    if not is_unblocked(grid, sx, sy) or not is_unblocked(grid, dx, dy):
        return []
    if is_destination(sx, sy, dest):
        return []

    visited = [[False] * GRID_W for _ in range(GRID_H)]
    parent = [[(-1, -1)] * GRID_W for _ in range(GRID_H)]
    distance = [[float("inf")] * GRID_W for _ in range(GRID_H)]
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
            nx, ny = x + dx_step, y + dy_step
            if not is_valid(nx, ny):
                continue
            if visited[ny][nx]:
                continue
            if not is_unblocked(grid, nx, ny):
                continue
            # New distance: use cost of entering the target cell
            new_dist = dist + grid.get_cost(nx, ny)
            if new_dist < distance[ny][nx]:
                distance[ny][nx] = new_dist
                parent[ny][nx] = (x, y)
                heapq.heappush(heap, (new_dist, nx, ny))
                # We don't return immediately – we want the shortest path, so wait until popped
    # Reconstruct path
    if distance[dy][dx] == float("inf"):
        return []
    path = []
    cx, cy = dest
    while parent[cy][cx] != (cx, cy):
        path.append((cx, cy))
        cx, cy = parent[cy][cx]
    path.append((cx, cy))
    path.reverse()
    return path


# weighted A*
def a_star_weighted(grid, src, dest):
    sx, sy = src
    dx, dy = dest
    if not is_valid(sx, sy) or not is_valid(dx, dy):
        return []
    if not is_unblocked(grid, sx, sy) or not is_unblocked(grid, dx, dy):
        return []
    if is_destination(sx, sy, dest):
        return []

    open_set = []
    heapq.heappush(open_set, (0, sx, sy))  # (f, x, y)
    g_score = [[float("inf")] * GRID_W for _ in range(GRID_H)]
    parent = [[(-1, -1)] * GRID_W for _ in range(GRID_H)]
    g_score[sy][sx] = 0
    parent[sy][sx] = (sx, sy)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while open_set:
        f, x, y = heapq.heappop(open_set)
        if (x, y) == (dx, dy):
            # Reconstruct path
            path = []
            cx, cy = dest
            while parent[cy][cx] != (cx, cy):
                path.append((cx, cy))
                cx, cy = parent[cy][cx]
            path.append((cx, cy))
            path.reverse()
            return path
        for dx_step, dy_step in directions:
            nx, ny = x + dx_step, y + dy_step
            if not is_valid(nx, ny) or not is_unblocked(grid, nx, ny):
                continue
            tentative_g = g_score[y][x] + grid.get_cost(nx, ny)
            if tentative_g < g_score[ny][nx]:
                parent[ny][nx] = (x, y)
                g_score[ny][nx] = tentative_g
                # Heuristic: Manhattan distance (min possible cost per step = 1)
                h = abs(nx - dx) + abs(ny - dy)
                f = tentative_g + h
                heapq.heappush(open_set, (f, nx, ny))
    return []  # no path
