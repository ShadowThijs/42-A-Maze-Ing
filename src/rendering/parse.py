"""Parsing of a maze.

Parses the maze output from the maze generation algorithm.
Outputs a valid to use structure for the maze.
"""

# North = 8
# East = 4
# South = 2
# West = 1

from dataclasses import dataclass
from enum import IntFlag, auto
from pathlib import Path

# ============================================================
# CONSTANTS & TYPES
# ============================================================

class Wall(IntFlag):
    NONE  = 0
    NORTH = 0b1000
    EAST  = 0b0100
    SOUTH = 0b0010
    WEST  = 0b0001

DIRECTION_MAP = {
    "N": Wall.NORTH,
    "E": Wall.EAST,
    "S": Wall.SOUTH,
    "W": Wall.WEST
}

OPPOSITE = {
    Wall.NORTH: Wall.SOUTH,
    Wall.SOUTH: Wall.NORTH,
    Wall.EAST:  Wall.WEST,
    Wall.WEST:  Wall.EAST
}

DIRECTION_DELTA = {
    "N": (-1, 0),
    "E": (0, 1),
    "S": (1, 0),
    "W": (0, -1)
}


@dataclass
class Position:
    row: int
    col: int

    def __add__(self, other):
        if isinstance(other, tuple):
            return Position(self.row + other[0], self.col + other[1])
        return Position(self.row + other.row, self.col + other.col)

    def __repr__(self):
        return f"({self.row}, {self.col})"


@dataclass
class Cell:
    walls: Wall

    def has_wall(self, direction: Wall) -> bool:
        return bool(self.walls & direction)

    def wall_list(self) -> list[str]:
        result = []
        if self.walls & Wall.NORTH: result.append("north")
        if self.walls & Wall.EAST:  result.append("east")
        if self.walls & Wall.SOUTH: result.append("south")
        if self.walls & Wall.WEST:  result.append("west")
        return result

    def to_hex(self) -> str:
        return f"{self.walls.value:X}"

    @classmethod
    def from_hex(cls, hex_char: str) -> "Cell":
        return cls(Wall(int(hex_char, 16)))


# ============================================================
# MAZE CLASS
# ============================================================

class Maze:
    def __init__(self):
        self.grid: list[list[Cell]] = []
        self.start: Position | None = None
        self.end: Position | None = None
        self.solution: str = ""
        self.rows: int = 0
        self.cols: int = 0

    @classmethod
    def from_file(cls, filepath: str | Path) -> "Maze":
        """Parse maze from file."""
        maze = cls()
        filepath = Path(filepath)

        with open(filepath, 'r') as f:
            content = f.read()

        # Split by empty line
        parts = content.strip().split("\n\n")

        if len(parts) < 2:
            raise ValueError("Invalid file format: missing separator between maze and metadata")

        # Parse maze grid
        maze_lines = parts[0].strip().split("\n")
        maze.grid = []
        for line in maze_lines:
            row = [Cell.from_hex(char) for char in line.strip()]
            maze.grid.append(row)

        maze.rows = len(maze.grid)
        maze.cols = len(maze.grid[0]) if maze.grid else 0

        # Parse metadata
        metadata = parts[1].strip().split("\n")

        if len(metadata) >= 1:
            start_parts = metadata[0].split(",")
            maze.start = Position(int(start_parts[0]), int(start_parts[1]))

        if len(metadata) >= 2:
            end_parts = metadata[1].split(",")
            maze.end = Position(int(end_parts[0]), int(end_parts[1]))

        if len(metadata) >= 3:
            maze.solution = metadata[2].strip()

        return maze

    def get_cell(self, pos: Position) -> Cell | None:
        """Get cell at position, or None if out of bounds."""
        if 0 <= pos.row < self.rows and 0 <= pos.col < self.cols:
            return self.grid[pos.row][pos.col]
        return None

    def is_valid_move(self, pos: Position, direction: str) -> bool:
        """Check if moving in direction from pos is valid (no wall blocking)."""
        cell = self.get_cell(pos)
        if cell is None:
            return False

        wall_dir = DIRECTION_MAP.get(direction.upper())
        if wall_dir is None:
            return False

        return not cell.has_wall(wall_dir)

    def validate_walls(self) -> list[dict]:
        """Check if all neighboring walls are consistent."""
        errors = []

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]

                # Check south/north consistency
                if r < self.rows - 1:
                    neighbor = self.grid[r + 1][c]
                    if cell.has_wall(Wall.SOUTH) != neighbor.has_wall(Wall.NORTH):
                        errors.append({
                            "pos1": Position(r, c),
                            "pos2": Position(r + 1, c),
                            "wall1": "south",
                            "wall2": "north"
                        })

                # Check east/west consistency
                if c < self.cols - 1:
                    neighbor = self.grid[r][c + 1]
                    if cell.has_wall(Wall.EAST) != neighbor.has_wall(Wall.WEST):
                        errors.append({
                            "pos1": Position(r, c),
                            "pos2": Position(r, c + 1),
                            "wall1": "east",
                            "wall2": "west"
                        })

        return errors

    def validate_solution(self) -> dict:
        """Validate the solution path."""
        if not self.solution or not self.start or not self.end:
            return {"valid": False, "error": "Missing solution, start, or end"}

        pos = Position(self.start.row, self.start.col)
        path = []
        errors = []

        for i, direction in enumerate(self.solution):
            direction = direction.upper()

            if direction not in DIRECTION_MAP:
                errors.append(f"Step {i}: Invalid direction '{direction}'")
                continue

            # Check for wall
            if not self.is_valid_move(pos, direction):
                errors.append(f"Step {i}: Wall blocks {direction} at {pos}")

            # Move anyway to continue validation
            delta = DIRECTION_DELTA[direction]
            pos = pos + delta
            path.append(pos)

            # Check bounds
            if self.get_cell(pos) is None:
                errors.append(f"Step {i}: Position {pos} out of bounds")
                break

        result = {
            "valid": len(errors) == 0 and pos.row == self.end.row and pos.col == self.end.col,
            "final_position": pos,
            "expected_end": self.end,
            "reached_end": pos.row == self.end.row and pos.col == self.end.col,
            "steps": len(self.solution),
            "errors": errors,
            "path": path
        }

        return result

    def to_hex_lines(self) -> list[str]:
        """Export maze back to hex format."""
        return ["".join(cell.to_hex() for cell in row) for row in self.grid]

    # ============================================================
    # VISUALIZATION (for testing)
    # ============================================================

    def render_ascii(self, show_path: bool = False, show_coords: bool = False) -> str:
        """Render maze as ASCII art."""
        if not self.grid:
            return ""

        # Build path positions set for highlighting
        path_positions = set()
        if show_path and self.solution and self.start:
            pos = Position(self.start.row, self.start.col)
            path_positions.add((pos.row, pos.col))
            for direction in self.solution:
                delta = DIRECTION_DELTA.get(direction.upper(), (0, 0))
                pos = pos + delta
                path_positions.add((pos.row, pos.col))

        result = []

        # Column headers
        if show_coords:
            header = "    " + "".join(f" {c % 10}  " for c in range(self.cols))
            result.append(header)

        for row_idx in range(self.rows):
            # Top line (north walls)
            top_line = "   +" if show_coords else "+"
            for col_idx in range(self.cols):
                cell = self.grid[row_idx][col_idx]
                top_line += "---+" if cell.has_wall(Wall.NORTH) else "   +"
            result.append(top_line)

            # Middle line (west/east walls + cell content)
            mid_line = f"{row_idx:2d} " if show_coords else ""
            for col_idx in range(self.cols):
                cell = self.grid[row_idx][col_idx]
                mid_line += "|" if cell.has_wall(Wall.WEST) else " "

                # Cell content
                pos = Position(row_idx, col_idx)
                if self.start and pos.row == self.start.row and pos.col == self.start.col:
                    mid_line += " S "
                elif self.end and pos.row == self.end.row and pos.col == self.end.col:
                    mid_line += " E "
                elif show_path and (row_idx, col_idx) in path_positions:
                    mid_line += " · "
                else:
                    mid_line += "   "

            # Rightmost east wall
            mid_line += "|" if self.grid[row_idx][-1].has_wall(Wall.EAST) else " "
            result.append(mid_line)

        # Bottom line (south walls of last row)
        bottom_line = "   +" if show_coords else "+"
        for col_idx in range(self.cols):
            cell = self.grid[-1][col_idx]
            bottom_line += "---+" if cell.has_wall(Wall.SOUTH) else "   +"
        result.append(bottom_line)

        return "\n".join(result)

    def __repr__(self):
        return f"Maze({self.rows}x{self.cols}, start={self.start}, end={self.end})"


# ============================================================
# MAIN
# ============================================================

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python maze_parser.py <maze_file>")
        print("\nCreating example file 'example_maze.txt' for testing...")

        # Create example file
        example_content = """9515391539551795151151153
EBABAE812853C1412BA812812
96A8416A84545412AC4282C2A
C3A83816A9395384453A82D02
96842A852AC07AAD13A8283C2
C1296C43AAB83AA92AA8686BA
92E853968428444682AC12902
AC3814452FA83FFF82C52C42A
85684117AFC6857FAC1383D06
C53AD043AFFFAFFF856AA8143
91441294297FAFD501142C6BA
AA912AC3843FAFFF82856D52A
842A8692A92B8517C4451552A
816AC384468285293917A9542
C416928513C443A828456C3BA
91416AA92C393A82801553AAA
A81292AA814682C6A8693C6AA
A8442C6C2C1168552C16A9542
86956951692C1455416928552
C545545456C54555545444556

1,1
19,14
SWSESWSESWSSSEESEEENEESESEESSSEEESSSEEENNENEE"""

        with open("example_maze.txt", "w") as f:
            f.write(example_content)

        filepath = "example_maze.txt"
    else:
        filepath = sys.argv[1]

    # Parse maze
    print(f"Loading maze from: {filepath}")
    print("=" * 60)

    maze = Maze.from_file(filepath)

    print(f"Maze dimensions: {maze.rows} x {maze.cols}")
    print(f"Start position:  {maze.start}")
    print(f"End position:    {maze.end}")
    print(f"Solution length: {len(maze.solution)} steps")
    print(f"Solution path:   {maze.solution[:50]}{'...' if len(maze.solution) > 50 else ''}")

    # Validate walls
    print("\n" + "=" * 60)
    print("WALL VALIDATION")
    print("=" * 60)

    wall_errors = maze.validate_walls()
    if wall_errors:
        print(f"✗ Found {len(wall_errors)} wall inconsistencies:")
        for err in wall_errors[:10]:
            print(f"  • {err['pos1']} {err['wall1']} ≠ {err['pos2']} {err['wall2']}")
        if len(wall_errors) > 10:
            print(f"  ... and {len(wall_errors) - 10} more")
    else:
        print("✓ All walls are consistent!")

    # Validate solution
    print("\n" + "=" * 60)
    print("SOLUTION VALIDATION")
    print("=" * 60)

    sol_result = maze.validate_solution()
    if sol_result["valid"]:
        print(f"✓ Solution is valid!")
        print(f"  Reached {sol_result['final_position']} in {sol_result['steps']} steps")
    else:
        print(f"✗ Solution is invalid!")
        print(f"  Final position: {sol_result['final_position']}")
        print(f"  Expected end:   {sol_result['expected_end']}")
        print(f"  Reached end:    {sol_result['reached_end']}")
        if sol_result["errors"]:
            print(f"  Errors:")
            for err in sol_result["errors"][:10]:
                print(f"    • {err}")

    # Render ASCII
    print("\n" + "=" * 60)
    print("ASCII VISUALIZATION (with solution path)")
    print("=" * 60)
    print(maze.render_ascii(show_path=True, show_coords=True))


if __name__ == "__main__":
    main()
