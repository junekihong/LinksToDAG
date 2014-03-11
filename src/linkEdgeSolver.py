#!/usr/bin/env python

from linkEdgeEncoder import *
from linklabel_table import *
from subprocess import call

# I handcoded a few rules in the linklabel_table in order to get our naive solver.
# This function exists mainly to give us a solver in order to test out the whole encoder-solver-decoder pipeline
def getLinkDirections_naive(links):
    linkDir = {}
    
    for i in xrange(len(links)):
        link = links[i]

        node1 = link[0]
        node2 = link[1]
        #level = link[2]
        label = link[3]
        
        decision = childParentLookup(node1, node2, label)
        
        if decision == None:
            #TODO
            #print node1, node2, label
            #exit(1)
            decision = True

        linkDir[tuple(link)] = decision

    return linkDir





def SCIP(zplFile, solutionFile = "/tmp/tempSolution"):
    #theCall =["scip", "-f", zplFile]
    theCall =["scip","-c", "read "+zplFile+" opt", "-c", "write solution "+solutionFile, "-c", "quit"]

    
    theCall.append("-l")
    theCall.append("/tmp/logFile")

    call(theCall)
    #scip -c "read knapsack.zpl opt" -c "write solution temp" -c "quit"

    print "SCIP CALL:"
    print " ".join(theCall)
    print

    return solutionFile

if __name__=="__main__":
    # Link Edge Encoder
    lines = readInput()
    (sentence, processedSentence, links) = getDataFromLinkParse(lines)

    wordTag = getWordTags(processedSentence)
    linkLabel = getLinkLabelMap(links)

    # Link Edge Solver
    #linkDir = getLinkDirections_naive(links)    
    
    #zplFile = "knapsack.zpl"
    #SCIP(zplFile)

    linksFile = "/tmp/links.txt"
    linksTXT(links,linksFile)
    
    zplFile = "/tmp/links.zpl"
    ZimplProgram(zplFile, linksFile)
    
    solutionFile = SCIP(zplFile)
