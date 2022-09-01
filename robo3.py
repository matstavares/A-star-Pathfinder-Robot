import sys
import time
import pygame
from queue import PriorityQueue
import random

TITLE = "Robo com A*"
HEURISTIC = 'manhattan' #if you want another, just implement it where it's in use
VARIANT = 'Greedy'
VARIANT = 'Dijkstra'
VARIANT = '' 

RELATORIO = 'report X - default variant.out'

MAPFILE = 'ambient.in'

POSITION_RANDOM = '' #keep it clean to NOT build a new one
POSITION_RANDOM = 'position_generated.out' #if has a output name, generate a new one
POSITION = 'position_generated.out' #reading generated
POSITION = 'position.in' #reading pattern and tools needed to generate a new random, Industries using first letter, tools the first 3

ITEMS_GENERATED = 'itens_generated.out'
ITEMS_INPUT = 'itens_generated.out' #reading generated
ITEMS_INPUT = '' #if empty, generate a item_generate

EXPANSIONED_CELLS = 0
RAIO = 4

BLACK = (0, 0, 0)
DARKBLUE = (0, 0, 139)
BLUE = (0, 0, 255)
LIGHTBLUE = (173,216,230)
DARKBROWN = (92, 64, 51)
BROWN = (139, 69, 19)
LIGHTBROWN = (227,127,36)
DARKGREY = (169, 169, 169)
DARKGREEN = (47, 79, 47)
GREEN = (0, 255, 0)
LIGHTGREEN = (144, 238, 144)
GREY = (128, 128, 128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
OCRE = (243, 199, 87)
TURQUOISE = (64, 224, 208)
WHITE = (255, 255, 255)
DARKYELLOW = (128, 128, 0)
YELLOW = (255, 255, 0)
LIGHTYELLOW = (255,191,0)

ITEM_IN_ROBO = {
  
}

TERRAIN_WEIGHT = {
  0 : 1,
  1 : 5,
  2 : 10,
  3 : 15,
  4 : float('inf')
}


TERRAIN_COLOR = {
  0 : GREEN,
  1 : BROWN,
  2 : BLUE,
  3 : OCRE,
  4 : BLACK
}

TERRAIN_COLOR_DARKER = {
  0 : DARKGREEN,
  1 : DARKBROWN,
  2 : DARKBLUE,
  3 : DARKYELLOW,
  4 : BLACK
}

TERRAIN_COLOR_LIGHTER = {
  0 : LIGHTGREEN,
  1 : LIGHTBROWN,
  2 : LIGHTBLUE,
  3 : LIGHTYELLOW,
  4 : BLACK
}

ITEM_QTD_MAX = {
  'Bat' : 20,
  'Sol': 10,
  'Suc': 8,
  'Ref': 6,
  'Pne' : 4
}


##########################

class Cell:
    def __init__(self, win, row, col, terrain, cell_height, cell_width, total_rows, total_cols, label):
        self.row = row
        self.col = col
        self.y = row * cell_height
        self.x = col * cell_width
        self.terrain = int(terrain)
        self.color = TERRAIN_COLOR[self.terrain]
        self.neighbors = []
        self.width = cell_width
        self.height = cell_height
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.item = ''
        self.g_score = float("inf")
        self.f_score = float("inf")
        self.closed = False
        self.open = False
        self.end = False
        self.start = False
        self.came_from = Cell
        self.label = label
        self.win = win
        self.path = []
        self.cost = 0
        self.move_from = ''
        

    def get_pos(self):
        return self.row, self.col

    def showItens(self):
        if self.item != '':
            itemLabel = self.label.render(self.item, True, BLACK)
            margin_x = round(( self.width - itemLabel.get_width() ) / 2)
            margin_y = round(( self.height - itemLabel.get_height() ) / 2)
            self.win.blit(itemLabel, (margin_x+self.x, margin_y+self.y))

    def is_closed(self):
        return self.closed

    def is_open(self):
        return self.open

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.start

    def is_end(self):
        return self.end

    def hasItem(self):
        return self.item != ''

    def reset(self):
        if not self.is_barrier():
            self.color = TERRAIN_COLOR[self.terrain]
        self.g_score = float("inf")
        self.f_score = float("inf")
        self.closed = False
        self.open = False
        self.end = False
        self.start = False
        self.path = []

    def reset_barrier(self):
        self.color = TERRAIN_COLOR[self.terrain]
        

    def get_weight(self):
        return TERRAIN_WEIGHT[self.terrain]

    def set_item(self, item):
        self.item = item

    def make_closed(self):
        self.color = TERRAIN_COLOR_LIGHTER[self.terrain]
        self.closed = True
        self.open = False

    def make_open(self):
        self.color = TERRAIN_COLOR_DARKER[self.terrain]
        self.open = True
        
    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.start = True

    def make_end(self):
        self.end = True

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.height))

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier() and not grid[self.row + 1][self.col].is_closed():
            self.neighbors.append(grid[self.row + 1][self.col])
            grid[self.row + 1][self.col].move_from = self

        #UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier() and not grid[self.row - 1][self.col].is_closed():
            self.neighbors.append(grid[self.row - 1][self.col])
            grid[self.row - 1][self.col].move_from = self

        # RIGHT
        if self.col < self.total_cols - 1 and not grid[self.row][self.col + 1].is_barrier() and not grid[self.row][self.col + 1].is_closed():
            self.neighbors.append(grid[self.row][self.col + 1])
            grid[self.row][self.col + 1].move_from = self

        #LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier() and not grid[self.row][self.col - 1].is_closed():
            self.neighbors.append(grid[self.row][self.col - 1])
            grid[self.row][self.col - 1].move_from = self
    
    def __lt__(self, other):
        return False

############################

def make_grid(win, cell_height, cell_width, lines, cols, label):
    grid = []

    with open(MAPFILE, "r") as f:
        mytiles = f.readlines()
        mytiles = [i.strip().replace(" ", "") for i in mytiles]
    
    for row, tiles in enumerate(mytiles):

        grid.append([])    

        for col, tile in enumerate(tiles):

            cell = Cell(win, row, col, tile, cell_height, cell_width, lines, cols, label)
            grid[row].append(cell)

    return grid


def draw_grid(win, cell_height, cell_width, rows, cols, height, width):
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * cell_height), (width, i * cell_height))
        for j in range(cols):
            pygame.draw.line(win, GREY, (j * cell_width, 0), (j * cell_width, height))


def draw(WINDOW, grid, industry_robo, cell_height, cell_width, rows, cols, height, width, label):
    WINDOW.fill(WHITE)
    for row in grid:
        for cell in row:
            cell.draw(WINDOW)
            cell.showItens()
    draw_grid(WINDOW, cell_height, cell_width, rows, cols, height, width)
    closest_industry(WINDOW, grid, industry_robo, label)
    pygame.display.update()


def get_clicked_pos(pos, cell_height, cell_width):
    x, y = pos

    row = y // cell_height
    col = x // cell_width

    return row, col

def h(p1, p2):
    
    y1, x1 = p1
    y2, x2 = p2
    
    if HEURISTIC == 'manhattan':
        return abs(y1 - y2) + abs(x1 - x2)

def reseting(grid):
    for row in grid:
        for cell in row:
            cell.reset()
        
def reseting_barrier(grid):
    for row in grid:
        for cell in row:
            cell.reset_barrier()

def reconstruct_path(start, current, draw):

    while current != start:
        current.make_path()
        current.came_from.path = current.path
        current.came_from.path.append(current)
        current = current.came_from
        draw()


def a_star(draw, grid, start, end):
    
    open_set = PriorityQueue()
  
    start.g_score = 0
    # but the start, knows only the heuristic
    start.f_score = h(start.get_pos(), end.get_pos())
    
    if VARIANT == 'Dijkstra':
        start.f_score = 0 # custo uniforme

    open_set.put((0, start))
    
    while not open_set.empty():
        
        # getting only the lowest cell from queue
        current = open_set.get()[1]
    
        if current == end:
            reconstruct_path(start, current, draw)
            return end

        current.update_neighbors(grid)

        temp_g_score = current.g_score + current.get_weight()

        if VARIANT == 'Gulosa':
            temp_g_score = 0
        
        for neighbor in current.neighbors:
            global EXPANSIONED_CELLS
            EXPANSIONED_CELLS += 1

            if temp_g_score < neighbor.g_score:
                neighbor.came_from = current
                neighbor.g_score = temp_g_score
                neighbor.f_score = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if VARIANT == 'Dijkstra':
                    neighbor.f_score = temp_g_score + 0 #custo uniforme
                
                # always add it
                open_set.put((neighbor.f_score, neighbor))
                neighbor.make_open()
        draw()

        if current != start:
            current.make_closed()

    # saw every neighbor, and didn't find a path
    return False


def get_lines_cols():
    with open(MAPFILE, "r") as f:
        mytiles = f.readlines()
        mytiles = [i.strip().split() for i in mytiles]
    
    for row, tiles in enumerate(mytiles):
        for col, tile in enumerate(tiles):
            lines = len(mytiles) # y
            cols = len(tiles) # x

            return lines, cols

def setting_industry(grid, lines, cols):
    global ITEM_IN_ROBO;
    with open(POSITION, "r") as f:
        mytiles = f.readlines()
        mytiles = [i.strip().split() for i in mytiles]
    
    industry_robo = {}
    last_tile = ''
    generated = False
    
    for row, tiles in enumerate(mytiles):
            for col, tile in enumerate(tiles):
                if POSITION_RANDOM == '':
                    if col == 0:
                        x = int(tile)
                    elif col == 1:
                        y = int(tile)
                    elif col == 2:
                        last_tile = tile[:1:]
                        industry_robo[tile[:1:]] = [(y, x), tile[:1:], (0,0)]
                    elif col == 3:
                        industry_robo[last_tile].append(int(tile))
                    elif col == 4:
                        industry_robo[last_tile].append(tile)
                        ITEM_IN_ROBO[industry_robo[last_tile][4]] = industry_robo[last_tile][3]

                else: # place industry and robo randomly
                    if col == 0:
                        while True:
                            y = random.randint(0, lines-1)
                            x = random.randint(0, cols-1)
                            if grid[y][x].item == '':
                                break
                        last_tile = tile[:1:]
                        industry_robo[tile[:1:]] = [(y, x), tile[:1:], (0,0)]
                    elif col == 1:
                        industry_robo[last_tile].append(int(tile))
                    elif col == 2:
                        industry_robo[last_tile].append(tile)
                        ITEM_IN_ROBO[industry_robo[last_tile][4]] = industry_robo[last_tile][3]

    if POSITION_RANDOM != '':
        with open(POSITION_RANDOM, "w") as f:
            for i in industry_robo:
                #output is always x,y instead of y,x
                if i == 'R':
                    f.write('{} {} {}\n'.format(industry_robo[i][0][1], industry_robo[i][0][0], i))
                else:
                    f.write('{} {} {} {} {}\n'.format(industry_robo[i][0][1], industry_robo[i][0][0], i, industry_robo[i][3], industry_robo[i][4]))

    return industry_robo

def closest_industry(win, grid, industry_robo, label):
    closest = float('inf')
    a = -1
    b = -1
    for i in industry_robo:
        y, x = industry_robo[i][0]
        
        if i != 'R':
            #makes industry not desapear after supply and can overwrite an item
            # grid[y][x].item = i

            heuristic = h(industry_robo['R'][0],(y,x))
            
            if heuristic < closest:
                a = y
                b = x

        else:
            itemLabel = label.render("Cost: {}".format(grid[y][x].cost), True, BLACK)
            win.blit(itemLabel, (5,5))
            

        itemLabel = label.render(i, True, BLACK)
        margin_x = round(( grid[y][x].width - itemLabel.get_width() ) / 2)
        margin_y = round(( grid[y][x].height - itemLabel.get_height() ) / 2)
        win.blit(itemLabel, (margin_x+grid[y][x].x, margin_y+grid[y][x].y))

    industry_robo['R'][2] = (a,b)


def popular_itens(grid, lines, cols):

    if ITEMS_INPUT == '':
        with open(ITEMS_GENERATED, "w") as f:
            for i in ITEM_QTD_MAX:
                for qtd in range(ITEM_QTD_MAX[i]):
                    while True:
                        l = random.randint(0,lines-1)
                        c = random.randint(0,cols-1)
                        if grid[l][c].item == '' and grid[l][c].terrain == 0:
                            grid[l][c].item = i
                            f.write('{} {} {}\n'.format(c, l, i)) #output is always x,y instead of y,x
                            break
    else:
        with open(ITEMS_INPUT, "r") as f:
            mytiles = f.readlines()
            mytiles = [i.strip().split() for i in mytiles]
            for row, tiles in enumerate(mytiles):
                for col, tile in enumerate(tiles):
                    if col == 0:
                        x = int(tile)
                    elif col == 1:
                        y = int(tile)
                    elif col == 2:
                        grid[y][x].item = tile
    
        
def found(item):
    global ITEM_IN_ROBO;

    for i in ITEM_IN_ROBO:
        if item == i:
            if ITEM_IN_ROBO[i] > 0:
               return True 
    
    return False

def look(draw, grid, start, end, lines, cols, raio):
    cells = 0
    closest = (float('inf'), float('inf'))
    
    for a in range(2*raio+1):
        for b in range(2*raio+1):
            y = (start.row + raio) - a
            x = (start.col + raio) - b 
            if y >= 0 and x >= 0 and y < lines and x < cols:
                cells += 1
                if grid[y][x].item != '':
                   if found(grid[y][x].item):
                        if h(start.get_pos(), closest) > h(start.get_pos(), (y,x)):
                            closest = (y,x)
    
    y, x = closest
    if y != float('inf') and x != float('inf'):
        if start.path == [] or (end.row != y or end.col != x):
            end = grid[y][x]
            if found(end.item):
                reseting(grid)
                a_star(draw, grid, start, end)
                return True
        else:
            return True
    return False

def industryOnTop(industry_robo):
    
    for i in industry_robo:
         if i != 'R':
            if industry_robo[i][0] == industry_robo['R'][0]:
                if ITEM_IN_ROBO[industry_robo[i][4]] <= 0:
                    ITEM_IN_ROBO.pop(industry_robo[i][4])
                    industry_robo.pop(i)
                    break


def RoboHasAllItems(industry_robo):
    global ITEM_IN_ROBO
    industries = []
    for i in industry_robo:
        if i != 'R':
            if ITEM_IN_ROBO[industry_robo[i][4]] <= 0:
                industries.append(industry_robo[i][0])
    while True:
        if len(industries) == 1:
            return industries[0]

        elif len(industries) > 1:
            if h(industry_robo['R'][0], industries[0]) > h(industry_robo['R'][0], industries[1]):
                industries.pop(0)
            else:
                industries.pop(1)
        
        else:
            return (-1, -1)

def move_to_next_industry(grid, draw, start, industry_robo):
    run = True

    industryOnTop(industry_robo)
    
    y, x = industry_robo['R'][2]
    if y == -1 or x == -1:
        run = False #there is no more industries, because Robo doesn't have an End coordinate
        with open(RELATORIO, "w") as f:
            f.write("Expanded nodes: {}\nTotal cost: {}\nUsing heuristic: {}\n".format(EXPANSIONED_CELLS, start.cost, HEURISTIC))

    a, b = RoboHasAllItems(industry_robo)
    if a != -1 and b != -1:
        end = grid[a][b]
        reseting(grid)
        a_star(draw, grid, start, end)

    else:
        
        reseting(grid)

        if len(ITEM_IN_ROBO) > 3:
            #moving cell by cell
            start.update_neighbors(grid)
            i = random.randint(0, len(start.neighbors)-1)
            end = start.neighbors[i]
        else:
            #moving large distance until find a item
            row = random.randint(0, len(grid)-1)
            col = random.randint(0, len(grid[0])-1)
            end = grid[row][col]

        a_star(draw, grid, start, end)

    return end, run


def move(grid, start, industry_robo):

    y, x = start.path[0].get_pos()
    end = grid[y][x]

    if start.path[-1].is_barrier():
        start.path = []
        return start, end

    cell = start.path.pop(-1)
    cell.cost = cell.get_weight() + start.cost
    industry_robo['R'][0] = (cell.row, cell.col)        
    
    return cell, end


def main():
    pygame.init()

    lines, cols = get_lines_cols()
    cell_width = 25
    cell_height = 20
    HEIGHT = lines * cell_height
    WIDTH = cols * cell_width
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.set_caption("A* Path Finding Algorithm")
    
    label = pygame.font.SysFont(None, 20)

    grid = make_grid(WINDOW, cell_height, cell_width, lines, cols, label)
    
    industry_robo = setting_industry(grid, lines, cols)

    popular_itens(grid, lines, cols)

    y, x = industry_robo['R'][0]
    start = grid[y][x]
    
    run = False
    gettingItems = False
    drawing = lambda: draw(WINDOW, grid, industry_robo, cell_height, cell_width, lines, cols, HEIGHT, WIDTH, label)

    while True:

        drawing()

        if run and not gettingItems:
            end, run = move_to_next_industry(grid, drawing, start, industry_robo)
            gettingItems = True

        if run and gettingItems:
            if look(drawing, grid, start, end, lines, cols, RAIO):
                
                for i in ITEM_IN_ROBO:
                    if start.item == i:
                        ITEM_IN_ROBO[i] -= 1
                        start.item = ''
            
            elif (start.path == []):
                gettingItems = False
            
            if (start.path != []):
                start, end = move(grid, start, industry_robo)
                
        
        time.sleep(.05) # remove to speed up

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

            if pygame.mouse.get_pressed()[0]: # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, cell_height, cell_width)
                cell = grid[row][col]

                if not start and not run:
                    start = cell
                    industry_robo['R'][0] = (row, col)
                    
                elif cell != start:
                    cell.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, cell_height, cell_width)
                cell = grid[row][col]
                cell.reset_barrier()
                if cell == start and not run:
                    start.item = ''
                    start = None
                    industry_robo['R'][0] = (-1,-1)

            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_c:
                    grid = make_grid(WINDOW, cell_height, cell_width, lines, cols, label)
                    industry_robo = setting_industry(grid, lines, cols)
                    popular_itens(grid, lines, cols)
                    y, x = industry_robo['R'][0]
                    start = grid[y][x]

                if event.key == pygame.K_r:
                    reseting_barrier(grid)
                
                if event.key == pygame.K_SPACE and start:
                    run = not run

    pygame.quit()

main()