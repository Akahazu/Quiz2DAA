# benchmark/benchmark.py
import random
import perfplot
from pathlib import Path
from game.algorithm import a_star_weighted, bfs_search, dijkstra_weighted

# Fixed scaling mock map with costs (reproducible)
class BenchmarkMap:
    def __init__(self, n, wall_ratio=0.15, seed=12345):
        self.width = n
        self.height = n
        rng = random.Random(seed)  # fixed seed for reproducibility
        
        self.walls = [[0] * n for _ in range(n)]
        self.costs = [[0] * n for _ in range(n)]
        
        for y in range(n):
            for x in range(n):
                if rng.random() < wall_ratio:
                    self.walls[y][x] = 1
                    self.costs[y][x] = 0
                else:
                    self.costs[y][x] = rng.randint(1, 5)
        
        # Ensure start and end are open
        self.walls[0][0] = 0
        self.costs[0][0] = 1
        self.walls[n-1][n-1] = 0
        self.costs[n-1][n-1] = 1

    def is_wall(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.walls[y][x] == 1
        return True

    def get_cost(self, x, y):
        if self.is_wall(x, y):
            return float('inf')
        return self.costs[y][x]

# Setup function for perfplot (N = grid dimension)
def setup_benchmark_instance(n):
    import game.algorithm as algorithm
    algorithm.GRID_W = n
    algorithm.GRID_H = n
    
    # Use a base seed that varies with N to ensure different maps per size,
    # but still deterministic
    mock_map = BenchmarkMap(n, wall_ratio=0.15, seed=12345 + n)
    src = (0, 0)
    dest = (n - 1, n - 1)
    return mock_map, src, dest

# Kernel wrappers – just return the path (perfplot only times the call)
def run_bfs(mock_map, src, dest):
    return bfs_search(mock_map, src, dest)

def run_a_star(mock_map, src, dest):
    return a_star_weighted(mock_map, src, dest)

def run_dijkstra(mock_map, src, dest):
    return dijkstra_weighted(mock_map, src, dest)

if __name__ == "__main__":
    Path("benchmark/output").mkdir(parents=True, exist_ok=True)
    # 7 sizes: 16^2=256, 1024^2=1,048,576 (spans > 2 orders of magnitude)
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    out = perfplot.bench(
        setup=setup_benchmark_instance,
        kernels=[run_bfs, run_a_star, run_dijkstra],
        labels=["BFS", "A*", "Dijkstra"],
        n_range=sizes,
        xlabel="Grid Dimension (N x N)",
        title="Pathfinding Runtime Scaling (Weighted Grid)",
        equality_check=None,  # Paths differ, so we don't compare
    )
    out.save("benchmark/output/pathfinding_runtime_scaling.png")
    out.show()
