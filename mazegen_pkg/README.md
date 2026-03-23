# mazegen

Reusable maze generator using the DFS recursive backtracker algorithm.

## Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Usage

```python
from mazegen import MazeGenerator

# Instantiate — does not generate yet
gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_=(19, 14),
    seed=42,       # optional; random if omitted
    perfect=True,  # True = unique path, False = multiple paths
)

# Generate the maze
gen.generate()

# Access the shortest solution path (N/E/S/W string)
print(gen.get_solution())  # e.g. 'SSENEENWW...'

# Access the grid structure
# grid[col][row] returns a dict: {'N': bool, 'E': bool, 'S': bool, 'W': bool}
# True = wall present in that direction
cell = gen.grid[0][0]
print(cell)  # {'N': True, 'E': False, 'S': False, 'W': True}

# Serialize to output-file format
print(gen.to_hex_string())
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `width` | int | Number of columns (≥ 2) |
| `height` | int | Number of rows (≥ 2) |
| `entry` | (int, int) | (col, row) of the entry cell |
| `exit_` | (int, int) | (col, row) of the exit cell |
| `seed` | int or None | Random seed for reproducibility |
| `perfect` | bool | True → perfect maze (unique path) |

## Output format

`to_hex_string()` returns a string where each character is a hex digit
encoding which walls are present on that cell:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

Example: `F` (1111) = all walls closed; `0` = all walls open.
