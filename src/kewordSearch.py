import csv
import heapq
import sys
import time
import numpy as np
import itertools as it
from collections import defaultdict


tags_index = defaultdict(list)
tags_index_count = defaultdict(int)
records_index = defaultdict(list)
input_file = open('data/Restaurants_London_England.tsv', 'r')
restaurants = csv.reader(input_file, delimiter='\t')


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


def kwSearchIF(args):

    if len(args) <= 0:
        return

    merged_list = []

    for tag in args:
        lines = tags_index[tag]
        
        if len(merged_list) == 0:
            merged_list = lines
        else:
            merged_list = merge(merged_list, lines)

    return merged_list


def kwSearchRaw(args, records_index):
    results = []
    for rest_id, rest_data in records_index.items():
        rest_tags = rest_data[2][6:]       
        rest_tags = set(rest_tags.split(','))
        
        if set(args).issubset(rest_tags):
            results.append(records_index[rest_id])

    return results




# ------------------ MAIN ---------------------- #

if len(sys.argv) <= 1:
    print("usage: task1.py tag1 tag2 ... tagk ")
    exit()
else:
    args = sys.argv[1:]

for key in tags_index:
    heapq.heapify(tags_index[key])

line_count = 1

for row in restaurants:

    records_index[line_count] = row

    # Extract comma sperated tags 
    tags = row[2][6:]       
    tags = tags.split(',') 

    # Measure tag frequency.
    # Store the index of the 
    for item in tags:
        tags_index_count[item] += 1
        if line_count not in tags_index[item]:
            heapq.heappush(tags_index[item], line_count)
    
    line_count += 1

print('number of keywords: ', len(tags_index_count))
print('Frequencies: ', [i for i in sorted(tags_index_count.values())], '\n')

t1 = time.time()
resultIF = kwSearchIF(args)
t2 = time.time()

t3 = time.time()
resultRaw = kwSearchRaw(args, records_index)
t4 = time.time()

print('')
print('kwSpaSearchIF: {} results, cost = {} seconds'.format(len(resultIF), t2 - t1))

for i in resultIF:
    print(', '.join(records_index[i]))

print('')
print('kwSpaSearchRaw: {} results, cost = {} seconds'.format(len(resultRaw), t4 - t3))

for i in resultRaw:
    print(', '.join(i))
