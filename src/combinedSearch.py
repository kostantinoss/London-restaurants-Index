# ------------------------------ #
# Konstantinos Chondralis  3109  #
# ------------------------------ #

import csv
import heapq
import sys
import time
import itertools as it
from collections import defaultdict


def getCoordinates(restaurant_record):
    pos = restaurant_record[1][10:]
    pos = pos.split(',')
    x = float(pos[0])
    y = float(pos[1])

    return x, y

def getTags(restaurant_record):
    tags = restaurant_record[2][6:]    
    tags = tags.split(',')
    
    return tags 


def load_data(restaurants):
    
    tags_index = defaultdict(list)
    restaurant_records = defaultdict(list)
    x_buckets = []
    y_buckets = []
    x_max = y_max = -10000.0
    x_min = y_min = 10000.0
    N = 50
    line = 1

    for key in tags_index:
        heapq.heapify(tags_index[key])

    for row in restaurants:
        # Extract comma sperated tags 
        # and load the into the inverted index.
        tags = row[2][6:]       
        tags = tags.split(',')
        for item in tags:
            if line not in tags_index[item]:
                heapq.heappush(tags_index[item], line)

        # Find min, max for each axis.
        x_coord, y_coord = getCoordinates(row)

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
    
    # Divide each axis inti 50 equal sections
    step_x = (x_max - x_min) / 50
    step_y = (y_max - y_min) / 50
    start_x = x_min
    start_y = y_min

    for i in range(0, 50):
        end_x = start_x + step_x
        end_y = start_y + step_y
        x_buckets.append([start_x, end_x])
        y_buckets.append([start_y, end_y])

        start_x = end_x
        start_y = end_y

    # Init grid
    grid = [[] for i in range(0, N)]

    for i in range(0, N):
        grid[i] = [[] for j in range(0, N)]
    
    # Populate grid
    for rest_id, rest_data in restaurant_records.items():
        x_coord, y_coord = getCoordinates(rest_data)
        i = j = 0
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
    

    return restaurant_records, tags_index, grid, x_buckets, y_buckets

def merge(list1, list2):
    if len(list1) < 0 or len(list2) < 0:
        return None

    i = j = 0
    result = []

    while i < len(list1) and j < len(list2):
        if list1[i] < list2[j]:
            i += 1
        elif list2[j] < list1[i]:
            j += 1
        else:
            result.append(list2[j])
            i += 1
            j += 1

    return result


def kwSpaSearchIF(tags, query_range,
                    tags_index, restaurant_records): 
    if len(tags) <= 0:
        return
    
    xmin = query_range[0]
    xmax = query_range[1]
    ymin = query_range[2]
    ymax = query_range[3]
    merged_list = result = []

    for tag in tags:
        lines = tags_index[tag]
        if len(merged_list) == 0:
            merged_list = lines
        else:
            merged_list = merge(merged_list, lines)

    for i in merged_list:
        rest_data = restaurant_records[i]
        x_coord, y_coord = getCoordinates(rest_data)
        if x_coord > xmin and x_coord < xmax:
            if y_coord > ymin and y_coord < ymax:
                result.append(restaurant_records[i])
    
    return result


def kwSpaSearchGrid(tags, query_range, tags_index,
                        x_buckets, y_buckets, grid,
                            restaurant_records):
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
    
    # Maps xmin and xmax coordinates from the
    # range query to the apropriate cells
    for x_coord in query_range[0:2]:
        for k in range(0, 50): 
            constrains = x_buckets[k]
            if x_coord > constrains[0] and x_coord < constrains[1]:
                xlist.append(k)
                break
    
    # Maps ymin and ymax coordinates from the 
    # range query to the apropriate cells
    for y_coord in query_range[2:]:
        for k in range(0, 50):
            constrains = y_buckets[k]
            if y_coord > constrains[0] and y_coord < constrains[1]:
                ylist.append(k)
                break

    for i in range(xlist[0], xlist[1] + 1):
        for j in range(ylist[0], ylist[1] + 1):
            for rest_id in grid[i][j]:
                rest_data = restaurant_records[rest_id]
                x_coord, y_coord = getCoordinates(rest_data)
                if x_coord > xmin and x_coord < xmax:
                    if y_coord > ymin and y_coord < ymax:
                        rest_tags = getTags(rest_data)                        
                        if set(tags).issubset(set(rest_tags)):
                            result.append(rest_data)

    return result


def kwSpaSearchRaw(tags, query_range,
                    tags_index, restaurant_records):
    results = []
    xmin = query_range[0]
    xmax = query_range[1]
    ymin = query_range[2]
    ymax = query_range[3]

    for rest_id, rest_data in restaurant_records.items():

        x_coord, y_coord = getCoordinates(rest_data)

        if x_coord > xmin and x_coord < xmax:
            if y_coord > ymin and y_coord < ymax:
                rest_tags = getTags(rest_data)
                
                if set(tags).issubset(set(rest_tags)):
                    results.append(restaurant_records[rest_id])
                    
    return results


# ------------------- MAIN ------------------------- #
# Check and sanitize the given command line arguments
if len(sys.argv) <= 1:
    print("usage: task2.py xmin xmax ymin ymax tag1 tag2 ...")
    exit()
else:
    tags_args = sys.argv[5:]
    range_args = [float(i) for i in sys.argv[1:5]]

print(range_args, tags_args)
input_file = open('assignment4/data/Restaurants_London_England.tsv', 'r')
restaurants = csv.reader(input_file, delimiter='\t')

restaurant_records, inverted_tag_index, grid, x_buckets, y_buckets = load_data(restaurants)

t1 = time.time()
resultIF = kwSpaSearchIF(tags_args, range_args,
                            inverted_tag_index, restaurant_records)
t2 = time.time()

t3 = time.time()
resultGrid = kwSpaSearchGrid(tags_args, range_args, inverted_tag_index,
                                x_buckets,y_buckets, grid, restaurant_records)
t4 = time.time()

t5 = time.time()
resultRaw = kwSpaSearchRaw(tags_args, range_args,
                    inverted_tag_index, restaurant_records)
t6 = time.time()

# Does some painting on the terminal.
print('')
print('kwSpaSearchIF: {} results, cost = {} seconds'.format(len(resultIF), t2 - t1))

for i in resultIF:
    print(', '.join(i))

print('')
print('kwSpaSearchGrid: {} results, cost = {} seconds'.format(len(resultGrid), t4 - t3))

for i in resultGrid:
    print(', '.join(i))

print('')
print('kwSpaSearchRaw:: {} results, cost = {} seconds'.format(len(resultRaw), t6 - t5))

for i in resultRaw:
    print(', '.join(i))