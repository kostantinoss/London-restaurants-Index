
import csv
import sys
import time
from collections import defaultdict


def getCoordinates(restaurant_record):
    pos = restaurant_record[1][10:]
    pos = pos.split(',')
    x = float(pos[0])
    y = float(pos[1])

    return x, y

# Loads restaurant records in a dictionary
# and finds min and max for each axis
def load_data(restaurants):
    restaurant_records = defaultdict(list)
    x_max = y_max = -10000.0
    x_min = y_min = 10000.0
    line = 0

    for row in restaurants:
        pos = row[1][10:]
        pos = pos.split(',')
        
        x_coord = float(pos[0])
        y_coord = float(pos[1])

        if x_coord > x_max:
            x_max = x_coord
        if x_coord < x_min:
            x_min = x_coord
        if y_coord > y_max:
            y_max = y_coord
        if y_coord < y_min:
            y_min = y_coord

        restaurant_records[line] = row
        line += 1

    return x_max, x_min, y_max, y_min, restaurant_records


def init_grid(N):
    grid = [[] for i in range(0, N)]

    for i in range(0, N):
        grid[i] = [[] for j in range(0, N)]
    
    return grid


# The folowing code iterates through all the restaurant 
# records and places each one in the aproproate 
# list in the grid. This is done by identifying the position 
# of the section that the coordinates fall in.
def populate_grid(grid, x_buckets, y_buckets):
    for rest_id, rest_data in restaurant_records.items():
        x_coord, y_coord = getCoordinates(rest_data)
        i = 0
        j = 0

        # Maps each pair of sections
        # with the corresponding cells
        for k in range(0, 50): 
            constrains = x_buckets[k]
            if x_coord > constrains[0] and x_coord < constrains[1]:
                i = k
                break
        
        for k in range(0, 50):
            constrains = y_buckets[k]
            if y_coord > constrains[0] and y_coord < constrains[1]:
                j = k
                break

        grid[i][j].append(rest_id)

    return grid


# The folowing code searches the grid for the desires restaurants.
# The query range given from the user is maped to the grid's cells using the 
# lists that hold information about the borders of each section.
def spaSearchGrid(query_range, grid, x_buckets, y_buckets) :
    result = []

    # x_list and y_list store the position of the cells that corespond 
    # to the boundary values of the range query. 
    # For exaple, if the qyery range is 50.546856 55.95297 -4.243601 1.387973,
    # x_list = [0, 49] and y_list = [0, 49] 
    xlist = []
    ylist = []
    xmin = query_range[0]
    xmax = query_range[1]
    ymin = query_range[2]
    ymax = query_range[3]

    # Map xmin and xmax coordinates from the
    # range query to the apropriate cells
    for x_coord in query_range[0:2]:
        for k in range(0, 50): 
            constrains = x_buckets[k]
            if x_coord >= constrains[0] and x_coord < constrains[1]:
                xlist.append(k)
                break

    # Map ymin and ymax coordinates from the 
    # range query to the apropriate cells
    for y_coord in query_range[2:]:
        for k in range(0, 50):
            constrains = y_buckets[k]
            if y_coord >= constrains[0] and y_coord < constrains[1]:
                ylist.append(k)
                break
    
    for i in range(xlist[0], xlist[1] + 1):
        for j in range(ylist[0], ylist[1] + 1):
            for rest_id in grid[i][j]:
                rest_data = restaurant_records[rest_id]
                x_coord, y_coord = getCoordinates(rest_data)
                if x_coord > xmin and x_coord < xmax:
                    if y_coord > ymin and y_coord < ymax:
                        result.append(restaurant_records[rest_id])

    return result


def spaSearchRaw(args, restaurants):
    results = []
    xmin = args[0]
    xmax = args[1]
    ymin = args[2]
    ymax = args[3]

    for rest_id, rest_data in restaurants.items():
        x_coord, y_coord = getCoordinates(rest_data)
        if x_coord > xmin and x_coord < xmax:
            if y_coord > ymin and y_coord < ymax:
                results.append(restaurants[rest_id])

    return results


# ------------------- MAIN ------------------------- #
# Check and sanitize the given command line arguments
if len(sys.argv) <= 1:
    print("usage: task2.py xmin xmax ymin ymax ")
    exit()
else:
    args = [float(i) for i in sys.argv[1:]]

input_file = open('data/Restaurants_London_England.tsv', 'r')
restaurants = csv.reader(input_file, delimiter='\t')

x_max, x_min, y_max, y_min, restaurant_records = load_data(restaurants)

# We divide the values of each axis (x ,y) into 50 equaly spaced sections.
# The folowing code constructs lists that contain the border values 
# of each section.
step_x = (x_max - x_min) / 50
step_y = (y_max - y_min) / 50
start_x = x_min
start_y = y_min

x_buckets = []
y_buckets = []

for i in range(0, 50):
    end_x = start_x + step_x
    end_y = start_y + step_y
    x_buckets.append([start_x, end_x])
    y_buckets.append([start_y, end_y])

    start_x = end_x
    start_y = end_y

grid = init_grid(50)
populate_grid(grid, x_buckets, y_buckets)

t1 = time.time()
resultsGrid = spaSearchGrid(args, grid, x_buckets, y_buckets)
t2 = time.time()

t3 = time.time()
resultsRaw = spaSearchRaw(args, restaurant_records)
t4 = time.time()

# Does some painting on the terminal.
print('bounds: {} {} {} {}'.format(x_min, x_max, y_min, y_max))
print('widths: {} {}'.format(x_max -x_min, y_max - y_min))

for i in range(0, 50):
    for j in range(0, 50):
        len_ = len(grid[i][j])
        if len_ > 0:
            print(i, j, len_)

print('')
print('spaSearchGrid: {} results, cost = {} seconds'.format(len(resultsGrid), t2 - t1))

for i in resultsGrid:
   print(', '.join(i))

print('')
print('spaSearchRaw: {} results, cost = {} seconds'.format(len(resultsRaw), t4 - t3))

for i in resultsRaw:
   print(', '.join(i))
