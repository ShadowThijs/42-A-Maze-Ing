"""A-Maze-Ing main."""


from algorithms import dfs, maze1
from rendering import render_console, render_mlx


def main() -> None:
    """Main method."""
    dfs()
    maze1()
    render_console()
    render_mlx()
    print("Hello from 42-a-maze-ing!")


if __name__ == "__main__":
    main()
