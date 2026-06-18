# benchmark/compare_seeds.py
import time
import csv
from pathlib import Path
import matplotlib.pyplot as plt

from game.settings import GRID_WIDTH, GRID_HEIGHT
from game.game_map import Map, wall_diningroom
from game.algorithm import dijkstra_weighted, a_star_weighted


def path_cost(grid, path):
    if not path:
        return float("inf")
    return sum(grid.get_cost(x, y) for x, y in path)


def run_seed(seed):
    # Generate map with this seed
    game_map = Map.from_seed(wall_diningroom, seed)

    # Player at the center of the grid
    player_tile = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

    # Define two start positions (as in your game)
    start_left = (4, 5)
    start_right = (21, 4)

    results = []
    for start_pos, start_label in [(start_left, "left"), (start_right, "right")]:
        # Dijkstra
        t0 = time.perf_counter()
        path_d = dijkstra_weighted(game_map, start_pos, player_tile)
        t_d = time.perf_counter() - t0
        cost_d = path_cost(game_map, path_d)

        # A*
        t0 = time.perf_counter()
        path_a = a_star_weighted(game_map, start_pos, player_tile)
        t_a = time.perf_counter() - t0
        cost_a = path_cost(game_map, path_a)

        # Record
        results.append(
            {
                "seed": seed,
                "start": start_label,
                "algorithm": "dijkstra",
                "time_sec": t_d,
                "cost": cost_d,
                "path_len": len(path_d) if path_d else 0,
            }
        )
        results.append(
            {
                "seed": seed,
                "start": start_label,
                "algorithm": "astar",
                "time_sec": t_a,
                "cost": cost_a,
                "path_len": len(path_a) if path_a else 0,
            }
        )
    return results


def main():
    # Parameters
    seeds = range(1, 101)  # 1 to 100 inclusive
    output_dir = Path("benchmark/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "seed_comparison.csv"

    print(f"Running benchmark over {len(seeds)} seeds...")
    all_results = []

    for seed in seeds:
        print(f"  Seed {seed}", end="", flush=True)
        res = run_seed(seed)
        all_results.extend(res)
        print(" ✓")

    # We will write it to CSV
    with open(csv_path, "w", newline="") as f:
        fieldnames = ["seed", "start", "algorithm", "time_sec", "cost", "path_len"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nResults saved to {csv_path}")

    # Produce a quick summary plot
    import pandas as pd

    df = pd.read_csv(csv_path)

    # Plot 1: Runtime comparison (boxplots by start and algorithm)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, start in zip(axes, ["left", "right"]):
        subset = df[df["start"] == start]
        # Pivot to compare dijkstra vs astar for each seed
        pivot = subset.pivot(index="seed", columns="algorithm", values="time_sec")
        pivot.plot.box(ax=ax, title=f"Runtime – {start} start")
        ax.set_ylabel("Time (seconds)")
        ax.grid(True)

    plt.tight_layout()
    plot1_path = output_dir / "runtime_boxplots.png"
    plt.savefig(plot1_path, dpi=150)
    print(f"Boxplot saved to {plot1_path}")

    # Plot 2: Cost difference (A* - Dijkstra) for each seed and start
    fig, ax = plt.subplots(figsize=(10, 6))
    for start in ["left", "right"]:
        sub = df[df["start"] == start]
        # Pivot to get cost columns
        cost_df = sub.pivot(index="seed", columns="algorithm", values="cost")
        # Compute difference (A* - Dijkstra) – ideally zero
        diff = cost_df["astar"] - cost_df["dijkstra"]
        ax.scatter(cost_df.index, diff, label=f"{start} start", alpha=0.7)
    ax.axhline(y=0, color="black", linestyle="--")
    ax.set_xlabel("Seed")
    ax.set_ylabel("Cost difference (A* - Dijkstra)")
    ax.set_title(
        "Path cost difference between A* and Dijkstra (should be 0 if both optimal)"
    )
    ax.legend()
    ax.grid(True)
    plot2_path = output_dir / "cost_difference.png"
    plt.savefig(plot2_path, dpi=150)
    print(f"Cost difference plot saved to {plot2_path}")

    # Also create a CSV with difference matrices for convenience
    diff_df = df.pivot_table(
        index=["seed", "start"], columns="algorithm", values=["time_sec", "cost"]
    )
    # Flatten multi-index columns
    diff_df.columns = ["_".join(col).strip() for col in diff_df.columns.values]
    diff_df.reset_index(inplace=True)
    diff_csv = output_dir / "seed_differences.csv"
    diff_df.to_csv(diff_csv, index=False)
    print(f"Difference matrix saved to {diff_csv}")

    print("\nBenchmark complete. Use the CSV files for further analysis.")


if __name__ == "__main__":
    main()
