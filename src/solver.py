#!/usr/bin/env python

from encoder import *
from subprocess import call
import os


def SCIP(zplFile, solutionFile = "/tmp/tempSolution"):
    #theCall =["scip", "-f", zplFile]
    theCall =["scip","-c", "read "+zplFile+" opt", "-c", "write solution "+solutionFile, "-c", "quit"]
    logFile = "/tmp/LinksToDAG_logFile.txt"
    theCall.append("-l")
    theCall.append(logFile)
    open(logFile, 'w+').close()


    call(theCall)
    #scip -c "read knapsack.zpl opt" -c "write solution temp" -c "quit"

    print "SCIP CALL:"
    print " ".join(theCall)
    print

    return solutionFile

if __name__=="__main__":
    linksFile = "/tmp/LinksToDAG_links.txt"
    zplFile = "/tmp/LinksToDAG_links.zpl"    
    solutionFile = "/tmp/LinksToDAG_solutions.txt"
    
    solutionsDirectory = "sol/"
    if not os.path.exists(solutionsDirectory):
        os.makedirs(solutionsDirectory)

    linksConllFile = solutionsDirectory+"links.conll"
    allowedLinksFile = solutionsDirectory+"allowedLinks.txt"

    open(linksFile, 'w+').close()
    open(zplFile, 'w+').close()
    open(solutionFile, 'w+').close()
    open(linksConllFile, 'w+').close()
    open(allowedLinksFile, 'w+').close()

    # Link Edge Encoder
    lines = readInput()
    (processedSentences, links) = getBatchDataFromLinkParses(lines)
    (sentences,sizeOfCorpus) = getSentencesFromProcessedSentences(processedSentences)


    #print sentences
    #print sizeOfCorpus

    
    wordTags = []
    linkLabels = []
    for i in xrange(len(sentences)):
        wordTags.append(getWordTags(processedSentences[i]))
        linkLabels.append(getLinkLabelMap(links[i]))
        linksTXT(links[i],linksFile, i)


    ZimplProgram(zplFile, linksFile, sizeOfCorpus)
    solutionFile = SCIP(zplFile, solutionFile)

    """
    print "SOLUTION FILE:"
    print solutionFile
    call(["cat", solutionFile])
    print
    """






