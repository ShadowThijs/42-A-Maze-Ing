"""Rendering init module."""

from rendering.console import render_console
from rendering.mlx import render_mlx
from rendering.colors import unicode_color

__all__ = ["render_console", "render_mlx", "unicode_color"]
