#!/usr/bin/env python

from utils import *

def printSentences():
    lines = readInput()
    sentences = getSentences(lines)

    for sentence in sentences:
        printedSentence = []    
        for word in sentence:
            word = word.split("\t")[1]
            printedSentence.append(word)

        printedSentence = " ".join(printedSentence)
        print printedSentence

if __name__ == "__main__":
    printSentences()
