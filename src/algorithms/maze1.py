"""Maze generation algorithm 1.

This is one of the algorithms we use to generate the maze
"""

import random


class CELL():
    """A single cell.

    Holds information about the current cell.
    """
    def __init__(self):
        """Init cell."""
        self.walls: dict[str, bool] = {
            "N": False,
            "E": False,
            "S": False,
            "W": False}
        self.visited: bool = False
        self.frozen: bool = False

    def update_wall(self,
                    N: bool,
                    E: bool,
                    S: bool,
                    W: bool,
                    freeze: bool = False
                    ):
        self.walls = {"N": N, "E": E, "S": S, "W": W}
        self.frozen = freeze


class CONFIG():
    """Information from config."""

    def __init__(self):
        self.Width: int = 0
        self.Height: int = 0
        self.Entry: list = [0, 0]
        self.Exit: list = [0, 0]
        self.Output: str = ""
        self.Perfect: bool = False
        self.Seed: int = 0
        self.Algorithm: int = 0
        self.Display: int = 0


def parse_config(file_name: str) -> CONFIG:
    """Parse the config file given as an argument."""

    config: CONFIG = CONFIG()

    with open(file_name, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            key, raw = line.split("=", 1)
            value = raw.strip()
            if key == "WIDTH":
                config.Width = int(value)
            elif key == "HEIGHT":
                config.Height = int(value)
            elif key == "ENTRY":
                config.Entry = [int(x) for x in value.split(",")]
            elif key == "EXIT":
                config.Exit = [int(x) for x in value.split(",")]
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

    return config


def place42(grid: list[list[CELL]], config: CONFIG) -> list[list[CELL]]:
    """Places 42 in center of maze."""
    cx: int = int(config.Width / 2)
    cy: int = int(config.Height / 2)
    four_x: int = cx - 3
    four_y: int = cy - 2
    two_x: int = cx + 3
    two_y: int = cy - 2
    grid[four_x][four_y].update_wall(True, True, False, True, True)
    grid[four_x][four_y+1].update_wall(False, True, False, True, True)
    grid[four_x][four_y+2].update_wall(False, True, True, False, True)
    grid[four_x+1][four_y+2].update_wall(True, False, True, False, True)
    grid[four_x+2][four_y+2].update_wall(True, False, False, True, True)
    grid[four_x+2][four_y+3].update_wall(False, True, False, True, True)
    grid[four_x+2][four_y+4].update_wall(False, True, True, True, True)

    grid[two_x][two_y].update_wall(True, True, True, False, True)
    grid[two_x][two_y].update_wall(True, False, True, False, True)
    grid[two_x][two_y].update_wall(True, False, False, True, True)
    grid[two_x][two_y].update_wall(False, True, False, True, True)
    grid[two_x][two_y].update_wall(False, False, True, True, True)
    grid[two_x][two_y].update_wall(True, False, True, False, True)
    grid[two_x][two_y].update_wall(True, True, False, False, True)
    grid[two_x][two_y].update_wall(False, True, False, True, True)
    grid[two_x][two_y].update_wall(False, True, True, False, True)
    grid[two_x][two_y].update_wall(True, False, True, False, True)
    grid[two_x][two_y].update_wall(True, False, True, True, True)
    return grid


def close_border(grid: list[list[CELL]], config: CONFIG) -> list[list[CELL]]:
    """Makes sure the borders are closed"""
    max_x: int = config.Width
    max_y: int = config.Height
    for i in range(0, max_x - 1):
        grid[i][0].walls["N"] = True
        grid[i][max_y - 1].walls["S"] = True
    for i in range(0, max_y - 1):
        grid[0][i].walls["W"] = True
        grid[max_x - 1][i].walls["E"] = True
    return grid


def maze1(file_name: str) -> None:
    """Maze 1 algorithm."""

    config: CONFIG = parse_config(file_name)
    random.seed(config.Seed)
    grid: list[list[CELL]] = [[CELL() for x in range(config.Height)]
                              for y in range(config.Width)]
    place42(grid, config)
    close_border(grid, config)
    print("Maze 1 algorithm")
