"""Maze file parser.

Parses hex-encoded maze files into a Maze dataclass for rendering.
"""

from dataclasses import dataclass, field
from enum import IntFlag


class Wall(IntFlag):
    """Wall directions as bit flags.

    Bit 0 = North, Bit 1 = East, Bit 2 = South, Bit 3 = West.
    """

    NONE = 0
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8


OPPOSITE: dict[Wall, Wall] = {
    Wall.NORTH: Wall.SOUTH,
    Wall.SOUTH: Wall.NORTH,
    Wall.EAST: Wall.WEST,
    Wall.WEST: Wall.EAST,
}

DIRECTION_DELTA: dict[str, tuple[int, int]] = {
    "N": (-1, 0),
    "E": (0, 1),
    "S": (1, 0),
    "W": (0, -1),
}

DIRECTION_WALL: dict[str, Wall] = {
    "N": Wall.NORTH,
    "E": Wall.EAST,
    "S": Wall.SOUTH,
    "W": Wall.WEST,
}


@dataclass
class Cell:
    """A single maze cell with wall information."""

    walls: Wall = Wall.NONE

    def has_wall(self, direction: Wall) -> bool:
        """Return True if this cell has a wall in the given direction."""
        return bool(self.walls & direction)


@dataclass
class Maze:
    """Parsed maze data.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        grid: 2D list of Cell objects indexed [row][col].
        entry: (row, col) tuple for the entry cell.
        exit: (row, col) tuple for the exit cell.
        solution: Solution path as a string of N/E/S/W characters.
        solution_cells: Set of (row, col) on the solution path.
        solution_directions: Direction at each cell on the solution path.
    """

    width: int = 0
    height: int = 0
    grid: list[list[Cell]] = field(default_factory=list)
    entry: tuple[int, int] = (0, 0)
    exit: tuple[int, int] = (0, 0)
    solution: str = ""
    solution_cells: set[tuple[int, int]] = field(default_factory=set)
    solution_directions: dict[tuple[int, int], list[str]] = field(
        default_factory=dict
    )

    def cell(self, row: int, col: int) -> Cell:
        """Return the cell at (row, col)."""
        return self.grid[row][col]

    def in_bounds(self, row: int, col: int) -> bool:
        """Return True if (row, col) is within the maze bounds."""
        return 0 <= row < self.height and 0 <= col < self.width


def _compute_solution_path(
    maze: Maze,
) -> tuple[set[tuple[int, int]], dict[tuple[int, int], list[str]]]:
    """Compute the set of cells and directions on the solution path."""
    cells: set[tuple[int, int]] = set()
    directions: dict[tuple[int, int], list[str]] = {}
    if not maze.solution:
        return cells, directions

    row, col = maze.entry
    cells.add((row, col))

    for ch in maze.solution:
        if (row, col) not in directions:
            directions[(row, col)] = []
        directions[(row, col)].append(ch)

        dr, dc = DIRECTION_DELTA[ch]
        row, col = row + dr, col + dc
        cells.add((row, col))

    return cells, directions


def parse_file(filepath: str) -> Maze:
    """Parse a hex-encoded maze file.

    Args:
        filepath: Path to the maze file.

    Returns:
        A Maze dataclass with all parsed data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is invalid.
    """
    with open(filepath, "r") as f:
        content = f.read().strip()

    parts = content.split("\n\n")
    if len(parts) < 2:
        raise ValueError("Invalid maze file: missing metadata section")

    grid_lines = parts[0].strip().split("\n")
    meta_lines = parts[1].strip().split("\n")

    if len(meta_lines) < 3:
        raise ValueError("Invalid maze file: need entry, exit, solution")

    height = len(grid_lines)
    width = len(grid_lines[0])

    grid: list[list[Cell]] = []
    for line in grid_lines:
        row: list[Cell] = []
        for ch in line:
            val = int(ch, 16)
            row.append(Cell(walls=Wall(val)))
        grid.append(row)

    entry_parts = meta_lines[0].split(",")
    exit_parts = meta_lines[1].split(",")
    entry = (int(entry_parts[1]), int(entry_parts[0]))
    exit_pos = (int(exit_parts[1]), int(exit_parts[0]))
    solution = meta_lines[2] if len(meta_lines) > 2 else ""

    maze = Maze(
        width=width,
        height=height,
        grid=grid,
        entry=entry,
        exit=exit_pos,
        solution=solution,
    )

    maze.solution_cells, maze.solution_directions = _compute_solution_path(
        maze
    )

    return maze
