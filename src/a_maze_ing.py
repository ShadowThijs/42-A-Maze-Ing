"""A-Maze-Ing — maze generator and renderer.

Usage:
    python3 a_maze_ing.py config.txt
"""

import sys

from algorithms.maze1 import CONFIG, generate_maze, parse_config, write_output
from algorithms.solve import bfs_solve
from rendering import render_console


def _run(config: CONFIG) -> None:
    """Generate, solve, write and render a maze.

    Args:
        config: Parsed maze configuration.
    """
    grid = generate_maze(config)
    solution = bfs_solve(grid, config)
    write_output(grid, config, solution)

    def regenerate() -> None:
        """Regenerate the maze with a new seed."""
        config.Seed += 1
        new_grid = generate_maze(config)
        new_solution = bfs_solve(new_grid, config)
        write_output(new_grid, config, new_solution)

    if config.Display == 1:
        try:
            from rendering import render_mlx
            render_mlx(config.Output)
        except ImportError:
            print(
                "MLX not available; falling back to console rendering.",
                file=sys.stderr,
            )
            render_console(config.Output, regenerate)
    else:
        render_console(config.Output, regenerate)


def main() -> None:
    """Entry point: parse arguments and run."""
    if len(sys.argv) != 2:
        print(
            f"Usage: {sys.argv[0]} config.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        config = parse_config(sys.argv[1])
    except FileNotFoundError:
        print(
            f"Error: config file not found: {sys.argv[1]}",
            file=sys.stderr,
        )
        sys.exit(1)
    except (ValueError, IndexError) as exc:
        print(f"Error: invalid config — {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        _run(config)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
