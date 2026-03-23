*This project has been created as part of the 42 curriculum by tklouwer.*

# A-Maze-ing

A maze generator and interactive visualiser written in Python.

## Description

A-Maze-ing generates mazes from a configuration file, writes them to a
hex-encoded output file, solves them with BFS, and renders them
interactively in the terminal using curses box-drawing characters.

Key features:

- **DFS recursive backtracker** maze generation (perfect or imperfect)
- Reproducible output via configurable random seed
- Embedded **"42" pattern** of fully-closed cells in the maze centre
- BFS shortest-path solver
- Interactive curses renderer with colour cycling and path toggle
- Reusable `mazegen` Python package (pip-installable)

## Instructions

### Requirements

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) (or pip)

### Install

```bash
make install
```

### Run

```bash
make run
# or directly:
python3 src/a_maze_ing.py config.txt
```

### Keys (terminal renderer)

| Key | Action |
|-----|--------|
| `g` | Re-generate a new maze |
| `s` | Show / hide solution path |
| `w` | Cycle wall colour |
| `b` | Cycle border colour |
| `p` | Cycle path colour |
| `q` | Quit |

### Lint

```bash
make lint
```

## Config file format

`config.txt` uses `KEY=VALUE` pairs (one per line). Lines starting with
`#` are ignored.

| Key | Required | Description | Example |
|-----|----------|-------------|---------|
| `WIDTH` | yes | Maze width in cells | `WIDTH=20` |
| `HEIGHT` | yes | Maze height in cells | `HEIGHT=15` |
| `ENTRY` | yes | Entry cell `col,row` | `ENTRY=0,0` |
| `EXIT` | yes | Exit cell `col,row` | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | Perfect maze? | `PERFECT=True` |
| `SEED` | no | Random seed | `SEED=42` |
| `ALGORITHM` | no | Algorithm selector (0=DFS) | `ALGORITHM=0` |
| `DISPLAY_MODE` | no | 0=console, 1=MLX | `DISPLAY_MODE=0` |

## Output file format

Each cell is encoded as one hex digit where bits represent closed walls:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

After the hex grid, a blank line separates three metadata lines:
1. Entry coordinates `col,row`
2. Exit coordinates `col,row`
3. Shortest path (N/E/S/W characters)

## Maze generation algorithm

The generator uses the **DFS recursive backtracker** (iterative):

1. Initialise all cells with all four walls closed.
2. Place the "42" pattern (fully-closed frozen cells) in the centre.
3. DFS from entry: pick a random unvisited non-frozen neighbour, remove
   the shared wall, push onto the stack.
4. After DFS, connect any remaining isolated cells.
5. For `PERFECT=False`, randomly remove ~15% of remaining inner walls.

This algorithm was chosen because it produces long winding paths (good
challenge), is simple to understand, and the iterative form handles large
mazes without hitting Python's recursion limit.

## Reusable module

The maze generation logic is packaged separately as `mazegen`.

### Installing

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### API

```python
from mazegen import MazeGenerator

gen = MazeGenerator(
    width=20, height=15,
    entry=(0, 0), exit_=(19, 14),
    seed=42, perfect=True,
)
gen.generate()

# Shortest path string (N/E/S/W)
print(gen.get_solution())

# Grid access: gen.grid[col][row] -> {'N': bool, 'E': bool, 'S': bool, 'W': bool}
# True = wall present in that direction
cell = gen.grid[0][0]

# Serialize to output-file format
print(gen.to_hex_string())
```

### Building from source

```bash
cd mazegen_pkg
pip install hatchling
python -m build
# or from repo root:
make build-pkg
```

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Think Labyrinth: Maze Algorithms](http://www.astrolog.org/labyrnth/algrithm.htm)
- [Python curses documentation](https://docs.python.org/3/library/curses.html)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)

### AI usage

Claude Code (Anthropic) was used to assist with:
- Designing the iterative DFS and BFS solver.
- Generating the curses rendering layer.
- Structuring the `mazegen` pip package.

All generated code was reviewed, tested, and integrated manually.

## Team

| Member | Role |
|--------|------|
| tklouwer | Maze generation, solver, rendering, packaging |

## Project management

Branches: `master` (stable) and `console-rendering` (renderer work).

Planning: requirements → algorithm selection (DFS backtracker) → core
generation → BFS solver → curses renderer → pip package → README.

What worked well: iterative DFS is clean and scales to large mazes.
What could be improved: 42 pattern placement for non-standard sizes.

Tools: Python 3.13, uv, flake8, mypy, curses, hatchling, Claude Code.
