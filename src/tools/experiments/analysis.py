#!/usr/bin/python

import os
from pprint import pprint


DIR = "/tmp/LinksToDAG_trial_sol/"

# Iterate over the files in the directory and store the ID of the run
IDs = []
results = []
for f in os.listdir(DIR):
    ID = int(f.split("_")[1].split(".")[0])
    IDs.append(ID)

    f = open(DIR+f)
    f = f.readlines()
    results.append(f)


# Find the biggest ID and look at its solution
biggest = max(IDs)
biggest_index = [i for i, j in enumerate(IDs) if j == biggest][0]
biggest_result = results[biggest_index]


# Iterate over the biggest solution and store the results
biggest_map = {}
type_map = {}
type_set = set()
for line in biggest_result:
    line = line.strip()
    if not line:
        continue
    biggest_map[line] = True
    
    line = line.split()
    ID = line[0]
    alignment = line[1]
    ID = "".join([c for c in ID if c.isupper()])
    type_map[(ID,alignment)] = type_map.get((ID,alignment), 0) + 1
    type_set.add(ID)
    #print ID, alignment
    

# For each link type group, find the majority classification 
# and then store the fraction of the link types in that group that agree with that majority.
type_analysis = []
for t in type_set:
    analysis = [t,"",""]

    one = type_map.get((t,"1"),0)
    two = type_map.get((t,"0"),0)
    majority = 0

    if one == two:
        analysis[1] = "BOTH"
        majority = one
    elif one > two:
        analysis[1] = "RIGHT"
        majority = one
    else:
        analysis[1] = "LEFT"
        majority = two
    
    analysis[2] = str(float(majority) / (one+two))
    type_analysis.append(tuple(analysis))


# Create a result directory to store the type analysis.
result_directory = "sol/type_agreement/"
if not os.path.exists(result_directory):
    os.makedirs(result_directory)


# Store the type analysis in a file:
type_analysis_file = "type_analysis.txt"
f = open(result_directory+type_analysis_file, "w+")
for t in type_analysis:
    f.write("\t".join(t)+"\n")
f.close()


# For all the other solutions smaller than the biggest run, 
# we compute the precision and recall of the links that match the one found in the biggest solution.
precision = {}
recall = {}
for ID,result in zip(IDs,results):
    precision_hits = 0
    recall_hits = 0
    current = {}

    for line in result:
        line = line.strip()
        if not line:
            continue
        if biggest_map.get(line, False):
            precision_hits += 1

        current[line] = True

    if len(current) > 0:
        precision[ID] = float(precision_hits) / len(current)

    for line in biggest_map:
        if current.get(line,False):
            recall_hits += 1

    if len(biggest_map) > 0:
        recall[ID] = float(recall_hits) / len(biggest_map)


# Create a result directory to store the precision and recall values.
result_directory = "sol/precision_recall/"
if not os.path.exists(result_directory):
    os.makedirs(result_directory)


# Store the precisions in a file.
precision_file = "precision.txt"
f = open(result_directory+precision_file, "w+")
for p in precision:
    f.write(str(p)+" "+str(precision[p])+"\n") 
f.close()


# Store the recalls in a file.
recall_file = "recall.txt"
f = open(result_directory+recall_file, "w+")
for r in recall:
    f.write(str(r)+" "+str(recall[r])+"\n")
f.close()


