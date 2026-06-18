import random
import perfplot
from game.algorithm import bfs_search, dijkstra_search

# 1. A scaling mock map class that matches your game_map structure
class BenchmarkMap:
    def __init__(self, n, wall_ratio=0.15):
        self.width = n
        self.height = n
        self.walls = [[1 if random.random() < wall_ratio else 0 for _ in range(n)] for _ in range(n)]

    def is_wall(self, cell_x, cell_y):
        if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
            return self.walls[cell_y][cell_x] == 1
        return True

# 2. Setup function required by perfplot for each size N
def setup_benchmark_instance(n):
    import game.algorithm as algorithm
    algorithm.GRID_W = n
    algorithm.GRID_H = n
    
    mock_map = BenchmarkMap(n, wall_ratio=0.15)
    src = (0, 0)
    dest = (n - 1, n - 1)
    
    # Ensure start and end points are never blocked by random walls
    mock_map.walls[src[1]][src[0]] = 0
    mock_map.walls[dest[1]][dest[0]] = 0
    
    return mock_map, src, dest

# 3. Kernel wrappers adjusted to receive the unpacked tuple elements
def run_bfs(mock_map, src, dest):
    return bfs_search(mock_map, src, dest)

def run_dijkstra(mock_map, src, dest):
    return dijkstra_search(mock_map, src, dest)

if __name__ == "__main__":
    out = perfplot.bench(
        setup=setup_benchmark_instance,
        kernels=[run_bfs, run_dijkstra],
        labels=["BFS - O(V + E)", "Dijkstra - O((V + E) log V)"],

        # 5 sizes spanning over two orders of magnitude (Vertices = N^2)
        n_range=[10**i for i in range(1, 4)],
        xlabel="Grid Dimension (N x N)",
        title="Pathfinding Performance Complexity Scaling Analysis",
        equality_check=None # Disable simple equality check because paths might take different routes but have identical step counts
    )
    
    # Save the generated graph directly for your report document
    out.save("benchmark/output/pathfinding_benchmark_perfplot.png")
    out.show()