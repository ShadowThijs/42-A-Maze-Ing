"""A-Maze-Ing main."""


from algorithms import dfs, maze1
from rendering import render_console
import sys


def main() -> None:
    """Main method."""
    argv: list[str] = sys.argv
    argc: int = len(argv)
    if (argc != 2):
        print("Please run like: " + argv[0] + " config.txt")
        exit()
    dfs()
    maze1(argv[1])
    # render_console('src/rendering/mazes/AI_3.txt')
    # render_mlx('src/rendering/mazes/AI_1.txt')
    print("Hello from 42-a-maze-ing!")


if __name__ == "__main__":
    main()
