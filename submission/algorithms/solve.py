"""BFS maze solver.

Finds the shortest path from entry to exit using breadth-first search.
"""

from collections import deque

from algorithms.maze import CELL, CONFIG, DELTA


def bfs_solve(
    grid: list[list[CELL]],
    config: CONFIG,
) -> str:
    """Find the shortest path from entry to exit using BFS.

    Args:
        grid: The maze grid (grid[col][row]).
        config: Maze configuration with Entry and Exit coordinates.

    Returns:
        String of N/E/S/W moves from entry to exit, or empty string if
        no path exists.
    """
    ex, ey = config.Entry[0], config.Entry[1]
    xx, xy = config.Exit[0], config.Exit[1]

    if [ex, ey] == [xx, xy]:
        return ""

    visited: set[tuple[int, int]] = {(ex, ey)}
    parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
    queue: deque[tuple[int, int]] = deque([(ex, ey)])

    while queue:
        x, y = queue.popleft()
        if (x, y) == (xx, xy):
            break
        for d in ["N", "S", "E", "W"]:
            if grid[x][y].walls[d]:
                continue
            dx, dy = DELTA[d]
            nx, ny = x + dx, y + dy
            if (
                not (0 <= nx < config.Width and 0 <= ny < config.Height)
                or (nx, ny) in visited
            ):
                continue
            visited.add((nx, ny))
            parent[(nx, ny)] = ((x, y), d)
            queue.append((nx, ny))

    if (xx, xy) not in parent:
        return ""

    moves: list[str] = []
    curr: tuple[int, int] = (xx, xy)
    while curr != (ex, ey):
        prev, d = parent[curr]
        moves.append(d)
        curr = prev

    return "".join(reversed(moves))


def dfs() -> None:
    """Stub kept for backward compatibility."""
    pass
