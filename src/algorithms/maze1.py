"""Maze generation using DFS recursive backtracker.

Generates perfect and imperfect mazes from a config file.
"""

import random
from typing import Optional

WALL_N: int = 1
WALL_E: int = 2
WALL_S: int = 4
WALL_W: int = 8

OPPOSITE: dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}
DELTA: dict[str, tuple[int, int]] = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}

# Pixel-art patterns for "4" and "2" (col_offset, row_offset)
FOUR_CELLS: list[tuple[int, int]] = [
    (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4),
]
TWO_CELLS: list[tuple[int, int]] = [
    (0, 0), (1, 0), (2, 0),
    (2, 1),
    (0, 2), (1, 2), (2, 2),
    (0, 3),
    (0, 4), (1, 4), (2, 4),
]


class CELL:
    """A single maze cell with wall information.

    Attributes:
        walls: Dict mapping direction to bool (True = wall present).
        visited: Whether DFS has visited this cell.
        frozen: Whether this cell is part of the 42 pattern (immutable).
    """

    def __init__(self) -> None:
        """Initialize cell with all walls closed."""
        self.walls: dict[str, bool] = {
            "N": True, "E": True, "S": True, "W": True,
        }
        self.visited: bool = False
        self.frozen: bool = False

    def update_wall(
        self,
        N: bool,
        E: bool,
        S: bool,
        W: bool,
        freeze: bool = False,
    ) -> None:
        """Set wall values and optionally freeze the cell.

        Args:
            N: North wall present.
            E: East wall present.
            S: South wall present.
            W: West wall present.
            freeze: Mark cell as frozen (part of 42 pattern).
        """
        self.walls = {"N": N, "E": E, "S": S, "W": W}
        self.frozen = freeze


class CONFIG:
    """Maze configuration loaded from a config file.

    Attributes:
        Width: Maze width in cells.
        Height: Maze height in cells.
        Entry: [col, row] entry coordinates.
        Exit: [col, row] exit coordinates.
        Output: Output filename.
        Perfect: Whether to generate a perfect maze.
        Seed: Random seed for reproducibility.
        Algorithm: Algorithm selector (0 = DFS).
        Display: Display mode (0 = console, 1 = MLX).
    """

    def __init__(self) -> None:
        """Initialize config with defaults."""
        self.Width: int = 0
        self.Height: int = 0
        self.Entry: list[int] = [0, 0]
        self.Exit: list[int] = [0, 0]
        self.Output: str = "maze.txt"
        self.Perfect: bool = True
        self.Seed: int = 0
        self.Algorithm: int = 0
        self.Display: int = 0


def parse_config(file_name: str) -> CONFIG:
    """Parse a KEY=VALUE config file.

    Args:
        file_name: Path to the config file.

    Returns:
        Populated CONFIG object.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If a required key is missing or malformed.
    """
    config: CONFIG = CONFIG()
    required: set[str] = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
    }
    found: set[str] = set()

    with open(file_name, "r") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Bad config line: {line!r}")
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            found.add(key)
            if key == "WIDTH":
                config.Width = int(value)
            elif key == "HEIGHT":
                config.Height = int(value)
            elif key == "ENTRY":
                parts = value.split(",")
                config.Entry = [int(parts[0]), int(parts[1])]
            elif key == "EXIT":
                parts = value.split(",")
                config.Exit = [int(parts[0]), int(parts[1])]
            elif key == "OUTPUT_FILE":
                config.Output = value
            elif key == "PERFECT":
                config.Perfect = value.lower() == "true"
            elif key == "SEED":
                config.Seed = int(value)
            elif key == "ALGORITHM":
                config.Algorithm = int(value)
            elif key == "DISPLAY_MODE":
                config.Display = int(value)

    missing = required - found
    if missing:
        raise ValueError(f"Missing required config keys: {missing}")

    if config.Width < 2 or config.Height < 2:
        raise ValueError("Maze dimensions must be at least 2x2")

    ec, er = config.Entry
    xc, xr = config.Exit
    if not (0 <= ec < config.Width and 0 <= er < config.Height):
        raise ValueError(f"ENTRY {ec},{er} is out of bounds")
    if not (0 <= xc < config.Width and 0 <= xr < config.Height):
        raise ValueError(f"EXIT {xc},{xr} is out of bounds")
    if config.Entry == config.Exit:
        raise ValueError("ENTRY and EXIT must be different")

    return config


def _in_bounds(x: int, y: int, config: CONFIG) -> bool:
    """Return True if (x, y) is inside the grid."""
    return 0 <= x < config.Width and 0 <= y < config.Height


def _place_digit(
    grid: list[list[CELL]],
    config: CONFIG,
    cells: list[tuple[int, int]],
    ox: int,
    oy: int,
) -> None:
    """Freeze cells for one digit and open interior walls between them.

    Each cell in *cells* is frozen with all walls closed first.  Then,
    for every pair of grid-adjacent cells within the digit, the shared
    wall is removed so the digit forms a single connected room.

    Args:
        grid: The maze grid (grid[col][row]).
        config: Maze configuration.
        cells: List of (col_offset, row_offset) relative to (ox, oy).
        ox: Origin column of the digit pattern.
        oy: Origin row of the digit pattern.
    """
    cell_set: set[tuple[int, int]] = set(cells)

    # Freeze every cell in the digit with all walls closed.
    for dc, dr in cells:
        col, row = ox + dc, oy + dr
        if _in_bounds(col, row, config):
            grid[col][row].update_wall(True, True, True, True, True)

    # Open the shared wall between adjacent cells inside the digit so the
    # digit forms a single open room (no internal walls).
    for dc, dr in cells:
        col, row = ox + dc, oy + dr
        if not _in_bounds(col, row, config):
            continue
        # East neighbour
        if (dc + 1, dr) in cell_set:
            ncol = ox + dc + 1
            if _in_bounds(ncol, row, config):
                grid[col][row].walls["E"] = False
                grid[ncol][row].walls["W"] = False
        # South neighbour
        if (dc, dr + 1) in cell_set:
            nrow = oy + dr + 1
            if _in_bounds(col, nrow, config):
                grid[col][row].walls["S"] = False
                grid[col][nrow].walls["N"] = False


def place42(grid: list[list[CELL]], config: CONFIG) -> bool:
    """Place the '42' pattern as closed rooms in the maze centre.

    Each digit is an isolated room: cells within the digit are open to
    each other but completely walled off from the rest of the maze.

    Args:
        grid: The maze grid (grid[col][row]).
        config: Maze configuration.

    Returns:
        True if the pattern was placed, False if maze is too small.
    """
    min_w = 10
    min_h = 7
    if config.Width < min_w or config.Height < min_h:
        print(
            f"Maze too small ({config.Width}x{config.Height}) "
            f"to display 42 pattern (needs {min_w}x{min_h}); skipping."
        )
        return False

    cx: int = config.Width // 2
    cy: int = config.Height // 2
    four_x: int = cx - 3
    four_y: int = cy - 2
    two_x: int = cx + 1
    two_y: int = cy - 2

    _place_digit(grid, config, FOUR_CELLS, four_x, four_y)
    _place_digit(grid, config, TWO_CELLS, two_x, two_y)

    return True


def _carve_dfs(
    grid: list[list[CELL]],
    config: CONFIG,
    start_x: int,
    start_y: int,
) -> None:
    """Iterative DFS that carves passages through the grid.

    Args:
        grid: The maze grid.
        config: Maze configuration.
        start_x: Starting column.
        start_y: Starting row.
    """
    stack: list[tuple[int, int]] = [(start_x, start_y)]
    grid[start_x][start_y].visited = True

    while stack:
        x, y = stack[-1]
        dirs: list[str] = ["N", "S", "E", "W"]
        random.shuffle(dirs)
        moved = False
        for d in dirs:
            dx, dy = DELTA[d]
            nx, ny = x + dx, y + dy
            if not _in_bounds(nx, ny, config):
                continue
            if grid[nx][ny].visited or grid[nx][ny].frozen:
                continue
            grid[x][y].walls[d] = False
            grid[nx][ny].walls[OPPOSITE[d]] = False
            grid[nx][ny].visited = True
            stack.append((nx, ny))
            moved = True
            break
        if not moved:
            stack.pop()


def _connect_isolated(
    grid: list[list[CELL]],
    config: CONFIG,
) -> None:
    """Connect any non-frozen cells not reached by the initial DFS.

    Args:
        grid: The maze grid.
        config: Maze configuration.
    """
    for x in range(config.Width):
        for y in range(config.Height):
            if grid[x][y].visited or grid[x][y].frozen:
                continue
            for d in ["N", "S", "E", "W"]:
                dx, dy = DELTA[d]
                nx, ny = x + dx, y + dy
                if (
                    _in_bounds(nx, ny, config)
                    and grid[nx][ny].visited
                    and not grid[nx][ny].frozen
                ):
                    grid[x][y].walls[d] = False
                    grid[nx][ny].walls[OPPOSITE[d]] = False
                    _carve_dfs(grid, config, x, y)
                    break


def _add_extra_passages(
    grid: list[list[CELL]],
    config: CONFIG,
    fraction: float = 0.15,
) -> None:
    """Remove extra walls to create an imperfect (multi-path) maze.

    Args:
        grid: The maze grid.
        config: Maze configuration.
        fraction: Fraction of inner walls to additionally remove.
    """
    inner = (
        (config.Width - 1) * config.Height
        + config.Width * (config.Height - 1)
    )
    target = max(1, int(inner * fraction))
    removed = 0
    attempts = 0
    max_attempts = target * 20

    dirs_and_deltas = [("E", 1, 0), ("S", 0, 1)]

    while removed < target and attempts < max_attempts:
        attempts += 1
        x = random.randint(0, config.Width - 1)
        y = random.randint(0, config.Height - 1)
        d, dx, dy = random.choice(dirs_and_deltas)
        nx, ny = x + dx, y + dy

        if not _in_bounds(nx, ny, config):
            continue
        if grid[x][y].frozen or grid[nx][ny].frozen:
            continue
        if not grid[x][y].walls[d]:
            continue

        grid[x][y].walls[d] = False
        grid[nx][ny].walls[OPPOSITE[d]] = False
        removed += 1


def cell_to_hex(cell: CELL) -> int:
    """Convert cell walls to hex digit value.

    Args:
        cell: The maze cell.

    Returns:
        Integer 0-15 encoding walls as bits (N=bit0, E=bit1, S=bit2, W=bit3).
    """
    val = 0
    if cell.walls["N"]:
        val |= WALL_N
    if cell.walls["E"]:
        val |= WALL_E
    if cell.walls["S"]:
        val |= WALL_S
    if cell.walls["W"]:
        val |= WALL_W
    return val


def generate_maze(config: CONFIG) -> list[list[CELL]]:
    """Generate a maze grid using DFS recursive backtracker.

    Args:
        config: Maze configuration.

    Returns:
        2D grid of CELL objects indexed [col][row].
    """
    random.seed(config.Seed)

    grid: list[list[CELL]] = [
        [CELL() for _ in range(config.Height)]
        for _ in range(config.Width)
    ]

    place42(grid, config)

    ex, ey = config.Entry[0], config.Entry[1]
    _carve_dfs(grid, config, ex, ey)
    _connect_isolated(grid, config)

    if not config.Perfect:
        _add_extra_passages(grid, config)

    return grid


def write_output(
    grid: list[list[CELL]],
    config: CONFIG,
    solution: str,
) -> None:
    """Write the maze to the output file.

    Args:
        grid: The maze grid (grid[col][row]).
        config: Maze configuration.
        solution: Solution path string (e.g. 'NNESWW').
    """
    lines: list[str] = []

    for row in range(config.Height):
        line = ""
        for col in range(config.Width):
            line += format(cell_to_hex(grid[col][row]), "X")
        lines.append(line)

    lines.append("")
    lines.append(f"{config.Entry[0]},{config.Entry[1]}")
    lines.append(f"{config.Exit[0]},{config.Exit[1]}")
    lines.append(solution)

    with open(config.Output, "w") as fh:
        fh.write("\n".join(lines) + "\n")


class MazeGenerator:
    """Reusable maze generator.

    Example usage::

        from mazegen import MazeGenerator

        gen = MazeGenerator(
            width=20, height=15,
            entry=(0, 0), exit_=(19, 14),
            seed=42, perfect=True,
        )
        gen.generate()
        print(gen.get_solution())   # e.g. 'SSEEN...'
        print(gen.to_hex_string())  # full output-file content

    Attributes:
        width: Number of columns.
        height: Number of rows.
        entry: (col, row) entry coordinate.
        exit_: (col, row) exit coordinate.
        seed: Random seed.
        perfect: Whether to produce a perfect maze.
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
        """Initialise the generator (does not generate yet).

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            entry: (col, row) of the entry cell.
            exit_: (col, row) of the exit cell.
            seed: Optional random seed for reproducibility.
            perfect: If True, produce a perfect maze (unique path).
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.seed = seed if seed is not None else random.randint(0, 2**32)
        self.perfect = perfect
        self._grid: Optional[list[list[CELL]]] = None
        self._solution: Optional[str] = None

    def generate(self) -> None:
        """Generate the maze (call before accessing grid/solution)."""
        from algorithms.solve import bfs_solve

        cfg = CONFIG()
        cfg.Width = self.width
        cfg.Height = self.height
        cfg.Entry = list(self.entry)
        cfg.Exit = list(self.exit_)
        cfg.Seed = self.seed
        cfg.Perfect = self.perfect
        cfg.Output = ""

        self._grid = generate_maze(cfg)
        self._solution = bfs_solve(self._grid, cfg)

    @property
    def grid(self) -> list[list[CELL]]:
        """The generated grid (grid[col][row]).

        Returns:
            2D list of CELL objects.

        Raises:
            RuntimeError: If generate() has not been called.
        """
        if self._grid is None:
            raise RuntimeError("Call generate() first")
        return self._grid

    def get_solution(self) -> str:
        """Return the shortest path from entry to exit.

        Returns:
            String of N/E/S/W characters.

        Raises:
            RuntimeError: If generate() has not been called.
        """
        if self._solution is None:
            raise RuntimeError("Call generate() first")
        return self._solution

    def to_hex_string(self) -> str:
        """Return the maze in output-file hex format.

        Returns:
            Multi-line string with hex grid, blank line, entry, exit, path.

        Raises:
            RuntimeError: If generate() has not been called.
        """
        if self._grid is None:
            raise RuntimeError("Call generate() first")

        lines: list[str] = []
        for row in range(self.height):
            line = ""
            for col in range(self.width):
                line += format(cell_to_hex(self._grid[col][row]), "X")
            lines.append(line)

        lines.append("")
        lines.append(f"{self.entry[0]},{self.entry[1]}")
        lines.append(f"{self.exit_[0]},{self.exit_[1]}")
        lines.append(self._solution or "")
        return "\n".join(lines) + "\n"


def maze1(file_name: str) -> None:
    """Run maze generation from a config file (legacy entry point).

    Args:
        file_name: Path to the config file.
    """
    from algorithms.solve import bfs_solve

    config = parse_config(file_name)
    grid = generate_maze(config)
    solution = bfs_solve(grid, config)
    write_output(grid, config, solution)
