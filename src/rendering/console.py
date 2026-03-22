"""Console rendering.

Renders the maze in the console using curses and box-drawing characters.
"""

import curses
import random
import time
from typing import Optional

from rendering.parser import Maze, Wall, parse_file

CELL_WIDTH: int = 2
CELL_HEIGHT: int = 1

THIN_H: str = "─"
THIN_V: str = "│"
THICK_H: str = "━"
THICK_V: str = "┃"

THIN_CORNERS: dict[tuple[bool, bool, bool, bool], str] = {
    (False, False, False, False): " ",
    (False, False, False, True): "╴",
    (False, False, True, False): "╷",
    (False, False, True, True): "┐",
    (False, True, False, False): "╶",
    (False, True, False, True): "─",
    (False, True, True, False): "┌",
    (False, True, True, True): "┬",
    (True, False, False, False): "╵",
    (True, False, False, True): "┘",
    (True, False, True, False): "│",
    (True, False, True, True): "┤",
    (True, True, False, False): "└",
    (True, True, False, True): "┴",
    (True, True, True, False): "├",
    (True, True, True, True): "┼",
}

THICK_CORNERS: dict[tuple[bool, bool, bool, bool], str] = {
    (False, False, False, False): " ",
    (False, False, False, True): "╸",
    (False, False, True, False): "╻",
    (False, False, True, True): "┓",
    (False, True, False, False): "╺",
    (False, True, False, True): "━",
    (False, True, True, False): "┏",
    (False, True, True, True): "┳",
    (True, False, False, False): "╹",
    (True, False, False, True): "┛",
    (True, False, True, False): "┃",
    (True, False, True, True): "┫",
    (True, True, False, False): "┗",
    (True, True, False, True): "┻",
    (True, True, True, False): "┣",
    (True, True, True, True): "╋",
}

PATH_CHARS: dict[tuple[bool, bool, bool, bool], str] = {
    (False, False, False, False): "·",
    (False, False, False, True): "╴",
    (False, False, True, False): "╷",
    (False, False, True, True): "┐",
    (False, True, False, False): "╶",
    (False, True, False, True): "─",
    (False, True, True, False): "┌",
    (False, True, True, True): "┬",
    (True, False, False, False): "╵",
    (True, False, False, True): "┘",
    (True, False, True, False): "│",
    (True, False, True, True): "┤",
    (True, True, False, False): "└",
    (True, True, False, True): "┴",
    (True, True, True, False): "├",
    (True, True, True, True): "┼",
}

OPPOSITE_DIR: dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}

AVAILABLE_COLORS: list[int] = [
    curses.COLOR_RED,
    curses.COLOR_GREEN,
    curses.COLOR_YELLOW,
    curses.COLOR_BLUE,
    curses.COLOR_MAGENTA,
    curses.COLOR_CYAN,
    curses.COLOR_WHITE,
]

COLOR_PAIR_WALL: int = 1
COLOR_PAIR_BORDER: int = 2
COLOR_PAIR_PATH: int = 3
COLOR_PAIR_ENTRY: int = 4
COLOR_PAIR_EXIT: int = 5
COLOR_PAIR_STATUS: int = 6

wall_color: int = curses.COLOR_WHITE
border_color: int = curses.COLOR_BLUE
path_color: int = curses.COLOR_GREEN
show_path: bool = True
maze: Optional[Maze] = None
maze_path: str = ""


def _init_colors() -> None:
    """Initialize curses color pairs."""
    curses.start_color()
    curses.use_default_colors()
    _update_color_pairs()


def _update_color_pairs() -> None:
    """Update color pairs with current color globals."""
    curses.init_pair(COLOR_PAIR_WALL, wall_color, -1)
    curses.init_pair(COLOR_PAIR_BORDER, border_color, -1)
    curses.init_pair(COLOR_PAIR_PATH, path_color, -1)
    curses.init_pair(COLOR_PAIR_ENTRY, curses.COLOR_GREEN, -1)
    curses.init_pair(COLOR_PAIR_EXIT, curses.COLOR_RED, -1)
    curses.init_pair(COLOR_PAIR_STATUS, curses.COLOR_BLACK, curses.COLOR_WHITE)


def _build_grid(
    m: Maze,
) -> tuple[list[list[str]], list[list[int]]]:
    """Build a character grid and color grid for the maze.

    Args:
        m: The parsed maze.

    Returns:
        A tuple of (character grid, color pair grid).
    """
    rows = m.height * 2 + 1
    cols = m.width * (CELL_WIDTH + 1) + 1
    chars: list[list[str]] = [[" "] * cols for _ in range(rows)]
    colors: list[list[int]] = [[0] * cols for _ in range(rows)]

    for r in range(m.height):
        for c in range(m.width):
            cell = m.cell(r, c)

            if cell.has_wall(Wall.NORTH):
                gy = r * 2
                border = r == 0
                h_ch = THICK_H if border else THIN_H
                pair = COLOR_PAIR_BORDER if border else COLOR_PAIR_WALL
                for i in range(CELL_WIDTH):
                    gx = c * (CELL_WIDTH + 1) + 1 + i
                    chars[gy][gx] = h_ch
                    colors[gy][gx] = pair

            if cell.has_wall(Wall.SOUTH):
                gy = (r + 1) * 2
                border = r == m.height - 1
                h_ch = THICK_H if border else THIN_H
                pair = COLOR_PAIR_BORDER if border else COLOR_PAIR_WALL
                for i in range(CELL_WIDTH):
                    gx = c * (CELL_WIDTH + 1) + 1 + i
                    chars[gy][gx] = h_ch
                    colors[gy][gx] = pair

            if cell.has_wall(Wall.WEST):
                gy = r * 2 + 1
                gx = c * (CELL_WIDTH + 1)
                border = c == 0
                chars[gy][gx] = THICK_V if border else THIN_V
                colors[gy][gx] = (
                    COLOR_PAIR_BORDER if border else COLOR_PAIR_WALL
                )

            if cell.has_wall(Wall.EAST):
                gy = r * 2 + 1
                gx = (c + 1) * (CELL_WIDTH + 1)
                border = c == m.width - 1
                chars[gy][gx] = THICK_V if border else THIN_V
                colors[gy][gx] = (
                    COLOR_PAIR_BORDER if border else COLOR_PAIR_WALL
                )

    _fill_junctions(m, chars, colors)
    return chars, colors


def _fill_junctions(
    m: Maze,
    chars: list[list[str]],
    colors: list[list[int]],
) -> None:
    """Compute and fill junction characters based on adjacent edges.

    Args:
        m: The parsed maze.
        chars: The character grid to fill.
        colors: The color pair grid to fill.
    """
    rows = len(chars)
    cols = len(chars[0])

    for jr in range(m.height + 1):
        for jc in range(m.width + 1):
            gy = jr * 2
            gx = jc * (CELL_WIDTH + 1)

            up = (
                gy > 0
                and chars[gy - 1][gx] in (THIN_V, THICK_V)
            )
            down = (
                gy < rows - 1
                and chars[gy + 1][gx] in (THIN_V, THICK_V)
            )
            left = (
                gx > 0
                and chars[gy][gx - 1] in (THIN_H, THICK_H)
            )
            right = (
                gx < cols - 1
                and chars[gy][gx + 1] in (THIN_H, THICK_H)
            )

            on_border = (
                jr == 0
                or jr == m.height
                or jc == 0
                or jc == m.width
            )
            key = (up, right, down, left)

            if on_border:
                chars[gy][gx] = THICK_CORNERS[key]
                colors[gy][gx] = COLOR_PAIR_BORDER
            else:
                chars[gy][gx] = THIN_CORNERS[key]
                colors[gy][gx] = COLOR_PAIR_WALL


def _path_directions(
    m: Maze, row: int, col: int
) -> tuple[bool, bool, bool, bool]:
    """Determine which directions the solution path connects at a cell.

    Args:
        m: The parsed maze.
        row: Cell row.
        col: Cell column.

    Returns:
        Tuple of (up, right, down, left) booleans.
    """
    up = False
    right = False
    down = False
    left = False

    dirs_from = m.solution_directions.get((row, col), [])
    for d in dirs_from:
        if d == "N":
            up = True
        elif d == "S":
            down = True
        elif d == "E":
            right = True
        elif d == "W":
            left = True

    for pos, dirs in m.solution_directions.items():
        for d in dirs:
            delta = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
            dr, dc = delta[d]
            if (pos[0] + dr, pos[1] + dc) == (row, col):
                opp = OPPOSITE_DIR[d]
                if opp == "N":
                    up = True
                elif opp == "S":
                    down = True
                elif opp == "E":
                    right = True
                elif opp == "W":
                    left = True

    return (up, right, down, left)


def _draw_maze(stdscr: "curses.window", m: Maze) -> None:
    """Draw the maze onto the curses window.

    Args:
        stdscr: The curses window.
        m: The parsed maze.
    """
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    chars, colors = _build_grid(m)
    grid_h = len(chars)
    grid_w = len(chars[0])

    offset_y = max(0, (max_y - grid_h - 2) // 2)
    offset_x = max(0, (max_x - grid_w) // 2)

    for gy in range(grid_h):
        sy = offset_y + gy
        if sy >= max_y - 1:
            break
        for gx in range(grid_w):
            sx = offset_x + gx
            if sx >= max_x:
                break
            ch = chars[gy][gx]
            pair = colors[gy][gx]
            if ch != " ":
                try:
                    stdscr.addstr(sy, sx, ch, curses.color_pair(pair))
                except curses.error:
                    pass

    for r in range(m.height):
        for c in range(m.width):
            sy = offset_y + r * 2 + 1
            sx = offset_x + c * (CELL_WIDTH + 1) + 1
            if sy >= max_y - 1 or sx + CELL_WIDTH > max_x:
                continue

            is_entry = (r, c) == m.entry
            is_exit = (r, c) == m.exit
            on_path = show_path and (r, c) in m.solution_cells

            if is_entry:
                try:
                    stdscr.addstr(
                        sy, sx, "EN",
                        curses.color_pair(COLOR_PAIR_ENTRY)
                        | curses.A_BOLD,
                    )
                except curses.error:
                    pass
            elif is_exit:
                try:
                    stdscr.addstr(
                        sy, sx, "EX",
                        curses.color_pair(COLOR_PAIR_EXIT)
                        | curses.A_BOLD,
                    )
                except curses.error:
                    pass
            elif on_path:
                key = _path_directions(m, r, c)
                p_ch = PATH_CHARS[key]
                content = p_ch.center(CELL_WIDTH)
                try:
                    stdscr.addstr(
                        sy, sx, content,
                        curses.color_pair(COLOR_PAIR_PATH)
                        | curses.A_BOLD,
                    )
                except curses.error:
                    pass


def _draw_status(stdscr: "curses.window") -> None:
    """Draw the vim-style status bar at the bottom.

    Args:
        stdscr: The curses window.
    """
    max_y, max_x = stdscr.getmaxyx()
    status = (
        " [w] wall color  [b] border color  [p] path color"
        "  [s] toggle path  [g] generate  [q] quit"
    )
    status = status[:max_x - 1]
    try:
        stdscr.addstr(
            max_y - 1, 0, status.ljust(max_x - 1),
            curses.color_pair(COLOR_PAIR_STATUS),
        )
    except curses.error:
        pass


def _loading_effect(stdscr: "curses.window") -> None:
    """Show a brief loading animation to simulate maze generation.

    Args:
        stdscr: The curses window.
    """
    max_y, max_x = stdscr.getmaxyx()
    msg = "Generating maze"
    cy = max_y // 2
    cx = max(0, (max_x - len(msg) - 3) // 2)

    for i in range(3):
        stdscr.clear()
        dots = "." * (i + 1)
        try:
            stdscr.addstr(cy, cx, msg + dots)
        except curses.error:
            pass
        stdscr.refresh()
        time.sleep(0.3)


def _random_color(exclude: int = -1) -> int:
    """Pick a random color, optionally excluding one.

    Args:
        exclude: Color index to exclude from selection.

    Returns:
        A random curses color constant.
    """
    choices = [c for c in AVAILABLE_COLORS if c != exclude]
    return random.choice(choices)


def _main_loop(stdscr: "curses.window") -> None:
    """Run the main curses event loop.

    Args:
        stdscr: The curses window.
    """
    global wall_color, border_color, path_color, show_path

    curses.curs_set(0)
    _init_colors()

    if maze is None:
        return

    _draw_maze(stdscr, maze)
    _draw_status(stdscr)
    stdscr.refresh()

    while True:
        key = stdscr.getch()

        if key == ord("q") or key == ord("Q"):
            break
        elif key == ord("w"):
            wall_color = _random_color(wall_color)
            _update_color_pairs()
        elif key == ord("b"):
            border_color = _random_color(border_color)
            _update_color_pairs()
        elif key == ord("p"):
            path_color = _random_color(path_color)
            _update_color_pairs()
        elif key == ord("s"):
            show_path = not show_path
        elif key == ord("g"):
            _loading_effect(stdscr)
        elif key == curses.KEY_RESIZE:
            pass
        else:
            continue

        _draw_maze(stdscr, maze)
        _draw_status(stdscr)
        stdscr.refresh()


def render_console(filepath: str) -> None:
    """Render the maze in the console using curses.

    Args:
        filepath: Path to the maze file to render.
    """
    global maze, maze_path
    maze_path = filepath
    maze = parse_file(filepath)
    curses.wrapper(_main_loop)
