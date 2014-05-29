#!/usr/bin/env python

import math, argparse, sys
import matplotlib.pyplot as plt
from pprint import pprint

parser = argparse.ArgumentParser(description="Plots a list of x,y points.")
parser.add_argument("-o", "--output", dest="output", default="sol/runtimes.png",
                    help="Specify an output file for the plot.")
parser.add_argument("-x","--x", dest="xLabel", default="Sentences",
                    help="Specify the x axis.")
parser.add_argument("-y","--y", dest="yLabel", default="Run Time (seconds)", 
                    help="Speciyf the y axis.")
parser.add_argument("strings", nargs="*")

args = parser.parse_args()


PE = "Precision: English"
RE = "Recall: English"
PR = "Precision: Russian"
RR = "Recall: Russian"


labels = []
file_lines = []
for filename in args.strings:

    label = filename.split("/")[-1]
    label = label.split(".")[0]
    label = label.split("_")[0]

    if len(label.split("#")) > 1:
        label = label.split("#")
        label = ": ".join(label)
    else:
        label += ": en"

    label = {"precision: en": PE,
             "recall: en": RE,
             "precision: ru": PR,
             "recall: ru": RR
             }.get(label, label)


    labels.append(label)
    
    lines = []
    f = open(filename)
    f = f.readlines()
    for line in f:
        line = line.strip()
        lines.append(line)
    file_lines.append(lines)




file_coord = []
for lines in file_lines:
    Xs = []
    Ys = []
    
    coord = []

    for line in lines:
        if not line:
            continue
        if line[0] == "#":
            continue

        line = line.split()
        x = float(line[0])
        y = float(line[1])
    
        coord.append((x,y))
    file_coord.append(coord)


# Get the minimum, maximum X values
xmax = None
xmin = 0
for coord in file_coord:
    temp_max = max(coord)
    if xmax == None or xmax < temp_max:
        xmax = temp_max

    temp_min = min(coord)
    if xmin > temp_min:
        xmin = temp_min
xmax = xmax[0]



plt.figure()
ax = plt.subplot(111)
ax.set_xlabel(args.xLabel)
ax.set_ylabel(args.yLabel)


for l,coord in zip(labels,file_coord):
    Xs = [elem[0] for elem in coord]
    Ys = [elem[1] for elem in coord]

    c = {PE:"DarkOrange",
         RE:"red",
         PR:"DeepSkyBlue",
         RR:"blue"
         }.get(l,"blue")


    m = {PE:"o",
         RE:"o",
         PR:"*",
         RR:"*"}.get(l,".")


    plt.plot(Xs,Ys, label=l, color=c, marker=m, linewidth=1.5)



ax.legend(loc='lower right')
plt.xlim(-0.015*xmax, xmax + 0.015*xmax)
plt.ylim(0,1.04)



#plt.show()
    

plt.savefig(args.output, bbox_inches='tight')

