import pygame
from queue import PriorityQueue
import time 

# -------------------- A* Algorithm --------------------

def h(p1, p2):
    # Heuristic: Manhattan distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def a_star(draw, grid, start, end, slow=False):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()
        if slow:
            time.sleep(0.05) 
        if current != start:
            current.make_closed()

    return False

# -------------------- Visualization Setup --------------------

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("AI Pathfinding Visualizer")

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# -------------------- Spot (Node) Class --------------------

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self): return self.color == RED
    def is_open(self): return self.color == GREEN
    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == ORANGE
    def is_end(self): return self.color == TURQUOISE

    def reset(self): self.color = WHITE
    def make_start(self): self.color = ORANGE
    def make_closed(self): self.color = RED
    def make_open(self): self.color = GREEN
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = TURQUOISE
    def make_path(self): self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

# -------------------- Grid Setup --------------------

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    if row >= rows:
        row = rows - 1
    if col >= rows:
        col = rows - 1
    return row, col

# -------------------- Clear Path Colors --------------------
def clear_path(grid):
    for row in grid:
        for spot in row:
            # Reset only visited or path cells (red, green, purple)
            if not (spot.is_barrier() or spot.is_start() or spot.is_end()):
                spot.reset()


# -------------------- Main Loop --------------------

def main(win, width):
    ROWS = 30
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True
    moving_start = False
    moving_end = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # --- LEFT CLICK (Place or Move Start/End/Barriers) ---
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

                # Dragging start node
                if moving_start:
                    start.reset()
                    start = spot
                    start.make_start()

                # Dragging end node
                elif moving_end:
                    end.reset()
                    end = spot
                    end.make_end()

                # Placing start
                elif not start and spot != end:
                    start = spot
                    start.make_start()

                # Placing end
                elif not end and spot != start:
                    end = spot
                    end.make_end()

                # Drawing barriers
                elif spot != end and spot != start:
                    spot.make_barrier()

            # --- RIGHT CLICK (Erase) ---
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            # --- Detect Drag Start ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    if spot == start:
                        moving_start = True
                        clear_path(grid)  # Clear path when moving start
                    elif spot == end:
                        moving_end = True
                        clear_path(grid)  # Clear path when moving end

            # --- Detect Drag End ---
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    moving_start = False
                    moving_end = False

            # --- Run or Clear ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    clear_path(grid) 
                    a_star(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_s and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    clear_path(grid) 
                    a_star(lambda: draw(win, grid, ROWS, width), grid, start, end, slow=True)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

# -------------------- Run Program --------------------

main(WIN, WIDTH)
