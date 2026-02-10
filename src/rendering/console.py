"""Console rendering.

Renders the maze in the console
"""


from rendering.colors import unicode_color

CELL_HEIGHT: int = 1
CELL_WIDTH: int  = 2

CELL_CHAR: str   = ' '
RESET: str       = u"\u001b[0m"

MAZE_WIDTH=20
MAZE_HEIGHT=20

def render_console(color: int = 9) -> None:
    """Render to console."""
    i: int = 0
    j: int = 0
    while (i < MAZE_HEIGHT):
        while (j < MAZE_WIDTH):
            if ((i == 0 or i == MAZE_HEIGHT - 1) and (j > 0 and j < MAZE_WIDTH - 1)):
                print((unicode_color(color) + CELL_CHAR + RESET) * CELL_WIDTH, end="")
            elif (j == 0 or j == MAZE_WIDTH - 1):
                print(unicode_color(color) + CELL_CHAR + RESET, end="")
            else:
                print(unicode_color(99) + CELL_CHAR * CELL_WIDTH  + RESET, end="")
            j += 1
        print()
        i += 1
        j = 0
    print("Rendering to console")
