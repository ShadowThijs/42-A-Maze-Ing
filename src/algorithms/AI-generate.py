import random
from datetime import datetime

def generate_maze(rows, cols, seed=42):
    """Generate a valid maze using recursive backtracking."""
    random.seed(seed)

    # Initialize grid - all walls present
    # Each cell stores: [north, east, south, west]
    grid = [[0xF for _ in range(cols)] for _ in range(rows)]

    visited = [[False] * cols for _ in range(rows)]

    def remove_wall(r1, c1, r2, c2):
        """Remove wall between two adjacent cells."""
        if r2 == r1 - 1:  # r2 is north of r1
            grid[r1][c1] &= ~0b1000  # remove north
            grid[r2][c2] &= ~0b0010  # remove south
        elif r2 == r1 + 1:  # r2 is south of r1
            grid[r1][c1] &= ~0b0010  # remove south
            grid[r2][c2] &= ~0b1000  # remove north
        elif c2 == c1 + 1:  # r2 is east of r1
            grid[r1][c1] &= ~0b0100  # remove east
            grid[r2][c2] &= ~0b0001  # remove west
        elif c2 == c1 - 1:  # r2 is west of r1
            grid[r1][c1] &= ~0b0001  # remove west
            grid[r2][c2] &= ~0b0100  # remove east

    def carve(r, c):
        """Recursive backtracking to carve passages."""
        visited[r][c] = True

        directions = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        random.shuffle(directions)

        for nr, nc in directions:
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                remove_wall(r, c, nr, nc)
                carve(nr, nc)

    # Start carving from (1, 1)
    carve(1, 1)

    return grid


def solve_maze(grid, start, end):
    """BFS to find solution path."""
    rows, cols = len(grid), len(grid[0])

    directions = {
        'N': (-1, 0, 0b1000),
        'S': (1, 0, 0b0010),
        'E': (0, 1, 0b0100),
        'W': (0, -1, 0b0001)
    }

    queue = [(start[0], start[1], "")]
    visited = {(start[0], start[1])}

    while queue:
        r, c, path = queue.pop(0)

        if (r, c) == end:
            return path

        for dir_name, (dr, dc, wall_bit) in directions.items():
            nr, nc = r + dr, c + dc

            if 0 <= nr < rows and 0 <= nc < cols:
                if (nr, nc) not in visited:
                    if not (grid[r][c] & wall_bit):  # No wall blocking
                        visited.add((nr, nc))
                        queue.append((nr, nc, path + dir_name))

    return None


def grid_to_hex(grid):
    """Convert grid to hex strings."""
    return ["".join(f"{cell:X}" for cell in row) for row in grid]


# Generate maze
rows, cols = random.randint(5, 30), random.randint(5, 30)
seed = int(datetime.now().timestamp())
grid = generate_maze(rows, cols, seed)

# Define start and end
start = (random.randint(5, rows), random.randint(5, cols))
end = (random.randint(5, rows), random.randint(5, cols))

# Remove entrance/exit walls for accessibility (optional internal points)
# Start and end are internal, so no border modification needed

# Solve
solution = solve_maze(grid, start, end)

# Output
for line in grid_to_hex(grid):
    print(line)
print()
print(f"{start[0]},{start[1]}")
print(f"{end[0]},{end[1]}")
print(solution)
