"""Algorithms init module."""

from algorithms.maze1 import MazeGenerator, generate_maze, maze1, parse_config
from algorithms.solve import bfs_solve, dfs

__all__ = [
    "dfs",
    "bfs_solve",
    "maze1",
    "parse_config",
    "generate_maze",
    "MazeGenerator",
]
