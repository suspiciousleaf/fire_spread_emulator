from turtle import Screen, Turtle, register_shape

# Run the program to open the window. Right click to create walls, left click to start a fire, and hit space bar to start the simulation.

# Size in pixels of each cell
CELL_SIZE = 20
# Size of the grid in cells
GRID_SIZE = 32
# Duration of each game tick, in ms. Low numbers may be limited by processing speed
TICK_DURATION = 5

# How many ticks a cell will burn for before being extinguished
FUEL_REMAINING = 40
# Cells will gain "heat" from neighbouring burning cells, this is the cumulative heat required to ignite
HEAT_TO_IGNITE = 5
# How many ticks an extinguished cell will sit before being refreshed
ASH_TIME = 80

# Import the icons and register the shapes to be used below.
tree = "icons\\tree.gif"
fire = "icons\\fire.gif"
ash = "icons\\ash.gif"
wall = "icons\\wall.gif"

register_shape(tree)
register_shape(fire)
register_shape(ash)
register_shape(wall)


class Cell(Turtle):
    """Class for each individual cell in the simulation."""

    def __init__(self, x, y):
        super().__init__()
        self.penup()
        self.shape(tree)
        self.goto(x, y)
        self.fuel_remaining = FUEL_REMAINING
        self.heat = 0
        self.ignited = False
        self.ash = False
        self.time_as_ash = 0
        self.neighbours = []
        self.ignited_this_tick = False
        self.wall = False

    def ignite(self):
        """Ignite the cell. 'ignited_this_tick' is used so that cells ignited this tick don't then ignite cells later in the loop."""
        self.ignited = True
        self.ignited_this_tick = True
        self.shape(fire)

    def highlight_neighbours(self):
        """Highlights neighbouring cells when igniting with the mouse, used for troubleshooting."""
        for cell in self.neighbours:
            cell.color("blue")

    def extinguish(self):
        """Extinguishes the cell when it has run out of fuel, turns it into ash and reset heat level."""
        self.heat = 0
        self.ignited = False
        self.ash = True
        self.shape(ash)

    def burn(self):
        """For cells that are ignited, continues the burn, consuming fuel, and extinguishes when fuel has run out."""
        if self.ignited_this_tick:
            self.ignited_this_tick = False
        self.fuel_remaining -= 1
        if not self.fuel_remaining:
            self.extinguish()

    def refresh(self):
        """When cells have been ash for a period of time, refreshes them into fresh trees with new fuel so the party can continue."""
        self.time_as_ash = 0
        self.shape(tree)
        self.fuel_remaining = FUEL_REMAINING
        self.ash = False

    def update_state(self, neighbours_burning):
        """Updates the cell, calls the above functions depending on fuel / heat / ash duration state."""
        if self.ignited:
            self.burn()
        elif self.ash:
            self.time_as_ash += 1
            if self.time_as_ash > ASH_TIME:
                self.refresh()
        elif neighbours_burning > 0:
            self.heat += neighbours_burning
            if self.heat >= HEAT_TO_IGNITE:
                self.ignite()


class CellManager:
    """Manages the grid of cells"""

    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.cells = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.create_cells(grid_size)
        self.add_neighbours()

    def get_starting_coordinates(self, value):
        """Generates the coordinates for each cell."""
        start_x = -(self.grid_size * CELL_SIZE) / 2 + CELL_SIZE / 2
        start_y = (self.grid_size * CELL_SIZE) / 2 - CELL_SIZE / 2
        row = (value - 1) // self.grid_size
        col = (value - 1) % self.grid_size
        x = start_x + col * CELL_SIZE
        y = start_y - row * CELL_SIZE
        return (x, y)

    def create_cells(self, grid_size):
        """Creates all the cells and positions them on the screen in a grid."""
        for i in range(1, grid_size**2 + 1):
            cell_position = self.get_starting_coordinates(i)
            new_cell = Cell(*cell_position)
            row = (i - 1) // grid_size
            col = (i - 1) % grid_size
            self.cells[row][col] = new_cell

    def all_cell_coords(self):
        """Generator to allow iterating through the nested list, to access each cell."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                yield (row, col)

    def add_neighbours(self):
        """Adds all neighbouring cells to each cell as a list of pointers."""
        for row, col in self.all_cell_coords():
            self.cells[row][col].neighbours.extend(self.find_neighbours(row, col))

    def find_neighbours(self, row, col):
        """Create pointers to cell neighbours."""
        neighbours = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                # Remove next two lines to have heat spread on diagonal, creates a less circular spread pattern
                if dr and dc:
                    continue
                nr = row + dr
                nc = col + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    neighbours.append(self.cells[nr][nc])
        return neighbours

    def count_neighbours_burning(self, row, col):
        """Counts the number of neighbouring cells that are burning, excluding those ignited this tick."""
        return sum(
            [
                1
                for neighbour in self.cells[row][col].neighbours
                if neighbour.ignited and not neighbour.ignited_this_tick
            ]
        )

    def update_cells(self):
        """Generates the state of the cells for the next game tick."""
        for row, col in self.all_cell_coords():
            cell = self.cells[row][col]
            if cell.wall:
                continue
            neighbours_burning = self.count_neighbours_burning(row, col)
            cell.update_state(neighbours_burning)


def ignite_cell(x, y):
    """Click on a cell to ignite it and start a fire!"""
    grid_x = int((x + (GRID_SIZE * CELL_SIZE) / 2) // CELL_SIZE)
    grid_y = int((-y + (GRID_SIZE * CELL_SIZE) / 2) // CELL_SIZE)
    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
        cell = cell_manager.cells[grid_y][grid_x]
        if not cell.ignited and not cell.ash:
            cell.ignite()
    screen.update()


def toggle_wall(x, y):
    """Right click to toggle a cell to become a wall that blocks fire."""
    grid_x = int((x + (GRID_SIZE * CELL_SIZE) / 2) // CELL_SIZE)
    grid_y = int((-y + (GRID_SIZE * CELL_SIZE) / 2) // CELL_SIZE)
    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
        cell = cell_manager.cells[grid_y][grid_x]
        if not cell.wall and not cell.ignited:
            cell.wall = True
            cell.shape(wall)
        elif cell.wall:
            cell.wall = False
            cell.shape(tree)
    screen.update()


screen = Screen()
screen.setup(width=GRID_SIZE * CELL_SIZE + 60, height=GRID_SIZE * CELL_SIZE + 60)
screen.tracer(0)

cell_manager = CellManager(GRID_SIZE)
screen.update()


def game_loop():
    cell_manager.update_cells()
    screen.update()
    screen.ontimer(game_loop, TICK_DURATION)


screen.onclick(ignite_cell)
screen.onscreenclick(toggle_wall, 3)
screen.listen()
screen.onkeypress(game_loop, "space")


screen.mainloop()
