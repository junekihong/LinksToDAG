#!/usr/bin/env python

import fileinput

def readInput():
    lines = []
    for line in fileinput.input():
        lines.append(line.strip())
    return lines

def getSentences(conll):
    sentence = []
    sentences = []
    for line in conll:
        if not line:
            sentences.append(sentence)
            sentence = []
        else:
            sentence.append(line)
    return sentences


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
