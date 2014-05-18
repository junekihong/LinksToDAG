#!/usr/bin/env python

import math
import matplotlib.pyplot as plt
import argparse
import sys


parser = argparse.ArgumentParser(description="Plots a list of x,y points.")
parser.add_argument("-o", "--output", dest="output", default="sol/runtimes.png",
                    help="Specify an output file for the plot.")
parser.add_argument("-x","--x", dest="xLabel", default="Sentences",
                    help="Specify the x axis.")
parser.add_argument("-y","--y", dest="yLabel", default="Run Time (seconds)", 
                    help="Speciyf the y axis.")
parser.add_argument("strings", nargs="*")

args = parser.parse_args()


lines = []
for f in args.strings:
    f = open(f)
    f = f.readlines()
    for line in f:
        line = line.strip()
        lines.append(line)



Xs = []
Ys = []


for line in lines:
    if not line:
        continue
    if line[0] == "#":
        continue


    line = line.split()
    x = float(line[0])
    y = float(line[1])
    
    Xs.append(x)
    Ys.append(y)


# Get the minimum, maximum X values
xmin = 0
xmax = max(Xs)


plt.figure()
ax = plt.subplot(111)
ax.set_xlabel(args.xLabel)
ax.set_ylabel(args.yLabel)

plt.plot(Xs,Ys)
plt.xlim(xmin, xmax)
plt.ylim(ymin=0)



#plt.show()
    

plt.savefig(args.output, bbox_inches='tight')

