#!/usr/bin/env python

import math
import matplotlib.pyplot as plt
from utils import readInput


lines = readInput()

Xs = []
Ys = []


for line in lines:
    line = line.split()
    x = float(line[0])
    y = float(line[1])
    
    Xs.append(x)
    Ys.append(y)
    


plt.figure()
ax = plt.subplot(111)
ax.set_xlabel('Sentences')
ax.set_ylabel('Run time')

plt.plot(Xs,Ys)
plt.xlim(xmin=0)
plt.ylim(ymin=0)



#plt.show()
plt.savefig('sol/runtimes.png', bbox_inches='tight')

