"""mazegen — reusable maze generator.

Quickstart::

    from mazegen import MazeGenerator

    gen = MazeGenerator(
        width=20, height=15,
        entry=(0, 0), exit_=(19, 14),
        seed=42, perfect=True,
    )
    gen.generate()

    # Shortest path as N/E/S/W string
    print(gen.get_solution())

    # Access individual cells
    # gen.grid[col][row] → dict with keys N, E, S, W (True = wall present)
    cell = gen.grid[0][0]
    print(cell)  # {'N': True, 'E': False, 'S': False, 'W': True}

    # Full output-file hex string
    print(gen.to_hex_string())
"""

import random
from collections import deque
from typing import Optional

__all__ = ["MazeGenerator"]

# Wall bit positions (matching output file format)
_WALL_N: int = 1
_WALL_E: int = 2
_WALL_S: int = 4
_WALL_W: int = 8

_OPPOSITE: dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}
_DELTA: dict[str, tuple[int, int]] = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}

# Pixel-art patterns for "4" and "2" (col_offset, row_offset)
_FOUR_CELLS: list[tuple[int, int]] = [
    (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4),
]
_TWO_CELLS: list[tuple[int, int]] = [
    (0, 0), (1, 0), (2, 0),
    (2, 1),
    (0, 2), (1, 2), (2, 2),
    (0, 3),
    (0, 4), (1, 4), (2, 4),
]


class _Cell:
    """Internal maze cell."""

    __slots__ = ("walls", "visited", "frozen")

    def __init__(self) -> None:
        self.walls: dict[str, bool] = {
            "N": True, "E": True, "S": True, "W": True,
        }
        self.visited: bool = False
        self.frozen: bool = False


def _in_bounds(x: int, y: int, w: int, h: int) -> bool:
    return 0 <= x < w and 0 <= y < h


def _place42(
    grid: list[list[_Cell]], width: int, height: int
) -> None:
    """Mark cells forming '42' as fully closed."""
    if width < 14 or height < 7:
        return
    cx = width // 2
    cy = height // 2
    four_x, four_y = cx - 3, cy - 2
    two_x, two_y = cx + 1, cy - 2

    for dc, dr in _FOUR_CELLS:
        col, row = four_x + dc, four_y + dr
        if _in_bounds(col, row, width, height):
            c = grid[col][row]
            c.walls = {"N": True, "E": True, "S": True, "W": True}
            c.frozen = True

    for dc, dr in _TWO_CELLS:
        col, row = two_x + dc, two_y + dr
        if _in_bounds(col, row, width, height):
            c = grid[col][row]
            c.walls = {"N": True, "E": True, "S": True, "W": True}
            c.frozen = True


def _carve_dfs(
    grid: list[list[_Cell]],
    width: int,
    height: int,
    sx: int,
    sy: int,
) -> None:
    """Iterative DFS carving passages from (sx, sy)."""
    stack: list[tuple[int, int]] = [(sx, sy)]
    grid[sx][sy].visited = True
    dirs = list(_DELTA.keys())

    while stack:
        x, y = stack[-1]
        random.shuffle(dirs)
        moved = False
        for d in dirs:
            dx, dy = _DELTA[d]
            nx, ny = x + dx, y + dy
            if not _in_bounds(nx, ny, width, height):
                continue
            nb = grid[nx][ny]
            if nb.visited or nb.frozen:
                continue
            grid[x][y].walls[d] = False
            nb.walls[_OPPOSITE[d]] = False
            nb.visited = True
            stack.append((nx, ny))
            moved = True
            break
        if not moved:
            stack.pop()


def _connect_isolated(
    grid: list[list[_Cell]], width: int, height: int
) -> None:
    """Connect any non-frozen unvisited cells to the main tree."""
    for x in range(width):
        for y in range(height):
            cell = grid[x][y]
            if cell.visited or cell.frozen:
                continue
            for d in ["N", "S", "E", "W"]:
                dx, dy = _DELTA[d]
                nx, ny = x + dx, y + dy
                if not _in_bounds(nx, ny, width, height):
                    continue
                nb = grid[nx][ny]
                if nb.visited and not nb.frozen:
                    cell.walls[d] = False
                    nb.walls[_OPPOSITE[d]] = False
                    _carve_dfs(grid, width, height, x, y)
                    break


def _add_extra_passages(
    grid: list[list[_Cell]],
    width: int,
    height: int,
    fraction: float = 0.15,
) -> None:
    """Randomly remove extra walls for an imperfect maze."""
    inner = (width - 1) * height + width * (height - 1)
    target = max(1, int(inner * fraction))
    removed = 0
    attempts = 0

    while removed < target and attempts < target * 20:
        attempts += 1
        x = random.randint(0, width - 2)
        y = random.randint(0, height - 1)
        d, dx, dy = ("E", 1, 0) if random.random() < 0.5 else ("S", 0, 1)
        nx, ny = x + dx, y + dy
        if not _in_bounds(nx, ny, width, height):
            continue
        if grid[x][y].frozen or grid[nx][ny].frozen:
            continue
        if not grid[x][y].walls[d]:
            continue
        grid[x][y].walls[d] = False
        grid[nx][ny].walls[_OPPOSITE[d]] = False
        removed += 1


def _bfs(
    grid: list[list[_Cell]],
    width: int,
    height: int,
    ex: int,
    ey: int,
    xx: int,
    xy: int,
) -> str:
    """BFS shortest path; returns N/E/S/W string."""
    if (ex, ey) == (xx, xy):
        return ""
    visited: set[tuple[int, int]] = {(ex, ey)}
    parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
    q: deque[tuple[int, int]] = deque([(ex, ey)])

    while q:
        x, y = q.popleft()
        if (x, y) == (xx, xy):
            break
        for d in ["N", "S", "E", "W"]:
            if grid[x][y].walls[d]:
                continue
            dx, dy = _DELTA[d]
            nx, ny = x + dx, y + dy
            if not _in_bounds(nx, ny, width, height) or (nx, ny) in visited:
                continue
            visited.add((nx, ny))
            parent[(nx, ny)] = ((x, y), d)
            q.append((nx, ny))

    if (xx, xy) not in parent:
        return ""

    moves: list[str] = []
    cur: tuple[int, int] = (xx, xy)
    while cur != (ex, ey):
        prev, d = parent[cur]
        moves.append(d)
        cur = prev
    return "".join(reversed(moves))


class MazeGenerator:
    """Generates a maze using the DFS recursive backtracker algorithm.

    The maze can be perfect (unique path between any two cells) or
    imperfect (additional passages create multiple routes).

    Example::

        gen = MazeGenerator(20, 15, (0, 0), (19, 14), seed=1, perfect=True)
        gen.generate()
        path = gen.get_solution()   # 'SSEEN...'
        grid = gen.grid             # grid[col][row] → {'N': bool, ...}

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: (col, row) of the entry cell.
        exit_: (col, row) of the exit cell.
        seed: Random seed for reproducibility (random if None).
        perfect: Produce a perfect maze when True.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        seed: Optional[int] = None,
        perfect: bool = True,
    ) -> None:
        if width < 2 or height < 2:
            raise ValueError("Dimensions must be at least 2x2")
        ec, er = entry
        xc, xr = exit_
        if not (_in_bounds(ec, er, width, height)
                and _in_bounds(xc, xr, width, height)):
            raise ValueError("entry/exit out of bounds")
        if entry == exit_:
            raise ValueError("entry and exit must differ")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.seed: int = seed if seed is not None else random.randint(0, 2**32)
        self.perfect = perfect
        self._grid: Optional[list[list[_Cell]]] = None
        self._solution: Optional[str] = None

    def generate(self) -> None:
        """Generate the maze. Must be called before accessing results."""
        random.seed(self.seed)
        w, h = self.width, self.height

        grid: list[list[_Cell]] = [
            [_Cell() for _ in range(h)] for _ in range(w)
        ]
        _place42(grid, w, h)
        _carve_dfs(grid, w, h, self.entry[0], self.entry[1])
        _connect_isolated(grid, w, h)
        if not self.perfect:
            _add_extra_passages(grid, w, h)

        self._grid = grid
        self._solution = _bfs(
            grid, w, h,
            self.entry[0], self.entry[1],
            self.exit_[0], self.exit_[1],
        )

    @property
    def grid(self) -> list[list[dict[str, bool]]]:
        """The generated maze grid.

        Returns:
            grid[col][row] → dict mapping 'N'/'E'/'S'/'W' to bool
            (True means a wall is present in that direction).

        Raises:
            RuntimeError: If generate() has not been called.
        """
        if self._grid is None:
            raise RuntimeError("Call generate() first")
        return [
            [cell.walls.copy() for cell in col]
            for col in self._grid
        ]

    def get_solution(self) -> str:
        """Return the shortest path from entry to exit.

        Returns:
            String of N/E/S/W characters, or '' if no path found.

        Raises:
            RuntimeError: If generate() has not been called.
        """
        if self._solution is None:
            raise RuntimeError("Call generate() first")
        return self._solution

    def to_hex_string(self) -> str:
        """Serialize the maze in output-file format.

        Format: hex grid (one row per line), blank line, entry x,y,
        exit x,y, solution path.

        Returns:
            Multi-line string ready to write to a file.

        Raises:
            RuntimeError: If generate() has not been called.
        """
        if self._grid is None:
            raise RuntimeError("Call generate() first")
        lines: list[str] = []
        for row in range(self.height):
            line = ""
            for col in range(self.width):
                c = self._grid[col][row]
                v = 0
                if c.walls["N"]:
                    v |= _WALL_N
                if c.walls["E"]:
                    v |= _WALL_E
                if c.walls["S"]:
                    v |= _WALL_S
                if c.walls["W"]:
                    v |= _WALL_W
                line += format(v, "X")
            lines.append(line)
        lines.append("")
        lines.append(f"{self.entry[0]},{self.entry[1]}")
        lines.append(f"{self.exit_[0]},{self.exit_[1]}")
        lines.append(self._solution or "")
        return "\n".join(lines) + "\n"
