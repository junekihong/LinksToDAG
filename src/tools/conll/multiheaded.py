#!/usr/bin/env python

import sys


filename = "sol/links_ru.conll"
if len(sys.argv) > 1:
    filename = sys.argv[1]

f = open(filename,"r")
f = f.readlines()


sentenceCount = 0
multiheadedSentenceCount = 0
sentence = []
heads = []
for line in f:
    line = line.strip()

    if not line:
        
        sentenceCount += 1

        for head in heads:
            if len(head) > 1:
                multiheadedSentenceCount += 1
                break

        sentence = []
        heads = []

        continue

    line = line.split()
    head = line[6].split(",")
    word = line[1]

    sentence.append(word)
    heads.append(tuple(head))
    
    #if len(head) > 1:
    #    print word, head


print multiheadedSentenceCount
#print sentenceCount
#print float(multiheadedSentenceCount) / float(sentenceCount)
