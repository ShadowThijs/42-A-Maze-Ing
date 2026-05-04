"""Algorithms init module."""

from algorithms.maze import MazeGenerator, generate_maze, maze, parse_config
from algorithms.solve import bfs_solve, dfs

__all__ = [
    "dfs",
    "bfs_solve",
    "maze",
    "parse_config",
    "generate_maze",
    "MazeGenerator",
]
