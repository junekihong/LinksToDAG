#!/usr/bin/python

import os
from pprint import pprint


DIR = "/tmp/LinksToDAG_trial_sol/"

IDs = []
results = []
for f in os.listdir(DIR):
    ID = int(f.split("_")[1].split(".")[0])
    IDs.append(ID)


    f = open(DIR+f)
    f = f.readlines()
    results.append(f)


biggest = max(IDs)
biggest_index = [i for i, j in enumerate(IDs) if j == biggest][0]
biggest_result = results[biggest_index]

biggest_map = {}
for line in biggest_result:
    line = line.strip()
    if not line:
        continue
    biggest_map[line] = True





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




result_directory = "sol/precision_recall/"
if not os.path.exists(result_directory):
    os.makedirs(result_directory)


precision_file = "precision.txt"
f = open(result_directory+precision_file, "w+")
#print "PRECISION:"
for p in precision:
    #print p, precision[p]
    f.write(str(p)+" "+str(precision[p])+"\n")    
print
#f.close()


recall_file = "recall.txt"
f = open(result_directory+recall_file, "w+")
#print "RECALL:"
for r in recall:
    #print r, recall[r]
    f.write(str(r)+" "+str(recall[r])+"\n")
#print
f.close()


