"""Maze generator using recursive backtracking.

Generates valid mazes with correct hexadecimal wall encoding
and solves them using BFS.
"""

import random
import sys
from collections import deque
from datetime import datetime

NORTH: int = 0x1
EAST: int = 0x2
SOUTH: int = 0x4
WEST: int = 0x8

OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST,
}

DELTA: dict[int, tuple[int, int]] = {
    NORTH: (-1, 0),
    SOUTH: (1, 0),
    EAST: (0, 1),
    WEST: (0, -1),
}

DIR_NAME: dict[int, str] = {
    NORTH: "N",
    SOUTH: "S",
    EAST: "E",
    WEST: "W",
}


def generate_maze(
    rows: int, cols: int, seed: int = 42
) -> list[list[int]]:
    """Generate a valid maze using recursive backtracking.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        seed: Random seed for reproducibility.

    Returns:
        A 2D grid where each cell is a hex value encoding its walls.
    """
    random.seed(seed)
    grid: list[list[int]] = [[0xF] * cols for _ in range(rows)]
    visited: list[list[bool]] = [
        [False] * cols for _ in range(rows)
    ]

    stack: list[tuple[int, int]] = [(1, 1)]
    visited[1][1] = True

    while stack:
        r, c = stack[-1]
        neighbors: list[tuple[int, int, int]] = []

        for wall, (dr, dc) in DELTA.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                neighbors.append((nr, nc, wall))

        if neighbors:
            nr, nc, wall = random.choice(neighbors)
            grid[r][c] &= ~wall
            grid[nr][nc] &= ~OPPOSITE[wall]
            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()

    return grid


def solve_maze(
    grid: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> str:
    """Find the shortest path through the maze using BFS.

    Args:
        grid: The maze grid.
        start: Start position as (row, col).
        end: End position as (row, col).

    Returns:
        A string of N/E/S/W directions, or empty string if unsolvable.
    """
    rows = len(grid)
    cols = len(grid[0])

    queue: deque[tuple[int, int, str]] = deque()
    queue.append((start[0], start[1], ""))
    seen: set[tuple[int, int]] = {start}

    while queue:
        r, c, path = queue.popleft()

        if (r, c) == end:
            return path

        for wall, (dr, dc) in DELTA.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if (nr, nc) not in seen and not (grid[r][c] & wall):
                    seen.add((nr, nc))
                    queue.append((nr, nc, path + DIR_NAME[wall]))

    return ""


def grid_to_hex(grid: list[list[int]]) -> list[str]:
    """Convert grid to hex strings.

    Args:
        grid: The maze grid.

    Returns:
        List of hex-encoded row strings.
    """
    return ["".join(f"{cell:X}" for cell in row) for row in grid]


def main() -> None:
    """Generate a maze and print it in the output file format."""
    rows = random.randint(10, 25)
    cols = random.randint(10, 25)
    seed = int(datetime.now().timestamp())

    grid = generate_maze(rows, cols, seed)

    start = (1, 1)
    end = (rows - 2, cols - 2)

    solution = solve_maze(grid, start, end)

    if not solution:
        print("Error: no solution found", file=sys.stderr)
        sys.exit(1)

    for line in grid_to_hex(grid):
        print(line)
    print()
    print(f"{start[1]},{start[0]}")
    print(f"{end[1]},{end[0]}")
    print(solution)


if __name__ == "__main__":
    main()
