"""MLX rendering.

Renders the maze using the MiniLibX graphical library.
"""

import random
from typing import Any

from mlx import Mlx

from rendering.parser import Maze, Wall, parse_file

CELL_SIZE_DEFAULT: int = 24
WALL_THICKNESS: int = 2
BORDER_THICKNESS: int = 4
PADDING: int = 60
STATUS_HEIGHT: int = 60

COLOR_BG: int = 0xFF1E1E2E
COLOR_WALL: int = 0xFFCDD6F4
COLOR_BORDER: int = 0xFF89B4FA
COLOR_PATH: int = 0xFFA6E3A1
COLOR_ENTRY: int = 0xFF94E2D5
COLOR_EXIT: int = 0xFFF38BA8
COLOR_STATUS_BG: int = 0xFF313244
COLOR_STATUS_FG: int = 0xFFCDD6F4

AVAILABLE_COLORS: list[int] = [
    0xFFCDD6F4,
    0xFFF38BA8,
    0xFFA6E3A1,
    0xFF89B4FA,
    0xFFF9E2AF,
    0xFFCBA6F7,
    0xFF94E2D5,
    0xFFFAB387,
]

DELTA: dict[str, tuple[int, int]] = {
    "N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1),
}


def _to_pixel_bytes(color: int) -> bytes:
    """Convert ARGB color to 4 bytes in BGRA order.

    Args:
        color: ARGB color value.

    Returns:
        4 bytes for one pixel.
    """
    return bytes([
        color & 0xFF,
        (color >> 8) & 0xFF,
        (color >> 16) & 0xFF,
        (color >> 24) & 0xFF,
    ])


class MlxRenderer:
    """Renders a maze using MiniLibX.

    Attributes:
        maze: The parsed maze to render.
        filepath: Path to the maze file.
        show_path: Whether to display the solution path.
        wall_color: Current wall color.
        border_color: Current border color.
        path_color: Current path color.
    """

    def __init__(self, filepath: str) -> None:
        """Initialize the MLX renderer.

        Args:
            filepath: Path to the maze file to render.
        """
        self.filepath: str = filepath
        self.maze: Maze = parse_file(filepath)
        self.show_path: bool = True
        self.wall_color: int = COLOR_WALL
        self.border_color: int = COLOR_BORDER
        self.path_color: int = COLOR_PATH

        self.mlx: Mlx = Mlx()
        self.mlx_ptr: Any = self.mlx.mlx_init()

        _, scr_w, scr_h = self.mlx.mlx_get_screen_size(
            self.mlx_ptr
        )
        self.cell_size: int = self._calc_cell_size(scr_w, scr_h)

        self.win_w: int = (
            self.maze.width * self.cell_size + PADDING * 3
        )
        self.win_h: int = (
            self.maze.height * self.cell_size
            + PADDING * 2
            + STATUS_HEIGHT
        )

        self.win_ptr: Any = self.mlx.mlx_new_window(
            self.mlx_ptr, self.win_w, self.win_h, "A-Maze-ing"
        )
        self.img_ptr: Any = None
        self.img_data: Any = None
        self.img_sl: int = 0

    def _calc_cell_size(self, scr_w: int, scr_h: int) -> int:
        """Calculate cell size that fits the maze on screen.

        Args:
            scr_w: Screen width in pixels.
            scr_h: Screen height in pixels.

        Returns:
            Cell size in pixels.
        """
        max_w = scr_w - 100
        max_h = scr_h - 100
        cs = CELL_SIZE_DEFAULT
        fit_w = (max_w - PADDING * 3) // self.maze.width
        fit_h = (
            (max_h - PADDING * 2 - STATUS_HEIGHT)
            // self.maze.height
        )
        return max(4, min(cs, fit_w, fit_h))

    def _create_image(self) -> None:
        """Create a new MLX image buffer."""
        if self.img_ptr is not None:
            self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.img_ptr = self.mlx.mlx_new_image(
            self.mlx_ptr, self.win_w, self.win_h
        )
        data, bpp, sl, fmt = self.mlx.mlx_get_data_addr(
            self.img_ptr
        )
        self.img_data = data
        self.img_sl = sl

    def _fill_rect(
        self, x: int, y: int, w: int, h: int, color: int
    ) -> None:
        """Fill a rectangle in the image buffer.

        Args:
            x: Top-left X coordinate.
            y: Top-left Y coordinate.
            w: Width.
            h: Height.
            color: ARGB color value.
        """
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.win_w, x + w)
        y1 = min(self.win_h, y + h)
        if x0 >= x1 or y0 >= y1:
            return

        row_w = x1 - x0
        pixel_bytes = _to_pixel_bytes(color)
        row_bytes = pixel_bytes * row_w
        sl = self.img_sl
        data = self.img_data

        for row in range(y0, y1):
            off = row * sl + x0 * 4
            data[off:off + row_w * 4] = row_bytes

    def _clear(self, color: int) -> None:
        """Clear the entire image with a color.

        Args:
            color: ARGB color value.
        """
        pixel_bytes = _to_pixel_bytes(color)
        full_row = pixel_bytes * self.win_w
        sl = self.img_sl
        data = self.img_data

        if sl == self.win_w * 4:
            full_img = full_row * self.win_h
            data[:len(full_img)] = full_img
        else:
            for row in range(self.win_h):
                off = row * sl
                data[off:off + self.win_w * 4] = full_row

    def _draw_walls(self) -> None:
        """Draw all maze walls."""
        m = self.maze
        cs = self.cell_size

        for r in range(m.height):
            for c in range(m.width):
                cell = m.cell(r, c)
                cx = PADDING + c * cs
                cy = PADDING + r * cs

                if cell.has_wall(Wall.NORTH):
                    is_b = r == 0
                    t = BORDER_THICKNESS if is_b else WALL_THICKNESS
                    clr = (
                        self.border_color
                        if is_b
                        else self.wall_color
                    )
                    self._fill_rect(
                        cx - t // 2, cy - t // 2,
                        cs + t, t, clr,
                    )

                if cell.has_wall(Wall.SOUTH):
                    is_b = r == m.height - 1
                    t = BORDER_THICKNESS if is_b else WALL_THICKNESS
                    clr = (
                        self.border_color
                        if is_b
                        else self.wall_color
                    )
                    self._fill_rect(
                        cx - t // 2, cy + cs - t // 2,
                        cs + t, t, clr,
                    )

                if cell.has_wall(Wall.WEST):
                    is_b = c == 0
                    t = BORDER_THICKNESS if is_b else WALL_THICKNESS
                    clr = (
                        self.border_color
                        if is_b
                        else self.wall_color
                    )
                    self._fill_rect(
                        cx - t // 2, cy - t // 2,
                        t, cs + t, clr,
                    )

                if cell.has_wall(Wall.EAST):
                    is_b = c == m.width - 1
                    t = BORDER_THICKNESS if is_b else WALL_THICKNESS
                    clr = (
                        self.border_color
                        if is_b
                        else self.wall_color
                    )
                    self._fill_rect(
                        cx + cs - t // 2, cy - t // 2,
                        t, cs + t, clr,
                    )

    def _draw_path(self) -> None:
        """Draw the solution path."""
        if not self.show_path:
            return

        m = self.maze
        cs = self.cell_size
        pw = max(2, cs // 4)

        for r, c in m.solution_cells:
            cx = PADDING + c * cs + cs // 2
            cy = PADDING + r * cs + cs // 2
            self._fill_rect(
                cx - pw // 2, cy - pw // 2,
                pw, pw, self.path_color,
            )

        r, c = m.entry
        for ch in m.solution:
            cx = PADDING + c * cs + cs // 2
            cy = PADDING + r * cs + cs // 2
            dr, dc = DELTA[ch]
            nr, nc = r + dr, c + dc
            nx = PADDING + nc * cs + cs // 2
            ny = PADDING + nr * cs + cs // 2

            if ch in ("N", "S"):
                self._fill_rect(
                    cx - pw // 2, min(cy, ny),
                    pw, abs(ny - cy), self.path_color,
                )
            else:
                self._fill_rect(
                    min(cx, nx), cy - pw // 2,
                    abs(nx - cx), pw, self.path_color,
                )

            r, c = nr, nc

    def _draw_markers(self) -> None:
        """Draw entry and exit markers."""
        m = self.maze
        cs = self.cell_size
        ms = max(4, cs // 3)

        for pos, color in [
            (m.entry, COLOR_ENTRY), (m.exit, COLOR_EXIT),
        ]:
            r, c = pos
            cx = PADDING + c * cs + cs // 2
            cy = PADDING + r * cs + cs // 2
            self._fill_rect(
                cx - ms // 2, cy - ms // 2, ms, ms, color,
            )

    def _draw_status(self) -> None:
        """Draw the status bar background."""
        sy = self.win_h - STATUS_HEIGHT
        self._fill_rect(
            0, sy, self.win_w, STATUS_HEIGHT, COLOR_STATUS_BG,
        )

    def _draw_status_text(self) -> None:
        """Draw status bar text using mlx_string_put."""
        sy = self.win_h - STATUS_HEIGHT + 18
        text = (
            "[W]all  [B]order  [P]ath color  "
            "[S]how path  [G]enerate  [ESC]quit"
        )
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 10, sy,
            COLOR_STATUS_FG, text,
        )

    def _render(self) -> None:
        """Render the full maze to the image and display it."""
        self._create_image()
        self._clear(COLOR_BG)
        self._draw_path()
        self._draw_walls()
        self._draw_markers()
        self._draw_status()

        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        self._draw_status_text()

    def _on_key(self, keycode: int, param: Any) -> None:
        """Handle key press events.

        Args:
            keycode: The key code pressed.
            param: Callback parameter (unused).
        """
        if keycode == 65307:
            self.mlx.mlx_loop_exit(self.mlx_ptr)
            return
        elif keycode == 119:
            self.wall_color = random.choice(AVAILABLE_COLORS)
        elif keycode == 98:
            self.border_color = random.choice(AVAILABLE_COLORS)
        elif keycode == 112:
            self.path_color = random.choice(AVAILABLE_COLORS)
        elif keycode == 115:
            self.show_path = not self.show_path
        elif keycode == 103:
            self.maze = parse_file(self.filepath)
        else:
            return

        self._render()

    def _on_close(self, param: Any) -> None:
        """Handle window close event.

        Args:
            param: Callback parameter (unused).
        """
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def _on_expose(self, param: Any) -> None:
        """Handle expose event to redraw.

        Args:
            param: Callback parameter (unused).
        """
        self._render()

    def run(self) -> None:
        """Start the MLX rendering loop."""
        self._render()
        self.mlx.mlx_key_hook(self.win_ptr, self._on_key, None)
        self.mlx.mlx_expose_hook(
            self.win_ptr, self._on_expose, None
        )
        self.mlx.mlx_hook(
            self.win_ptr, 33, 0, self._on_close, None
        )
        self.mlx.mlx_loop(self.mlx_ptr)
        self._cleanup()

    def _cleanup(self) -> None:
        """Clean up MLX resources."""
        if self.img_ptr is not None:
            self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_release(self.mlx_ptr)


def render_mlx(filepath: str) -> None:
    """Render the maze using MLX.

    Args:
        filepath: Path to the maze file to render.
    """
    renderer = MlxRenderer(filepath)
    renderer.run()
