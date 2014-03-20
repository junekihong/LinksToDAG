#!/usr/bin/env python

from linkEdgeEncoder import *
from linkEdgeSolver import *
from linkEdgeDecoder import *
import argparse

if __name__=="__main__":
    linksFile = "/tmp/LinksToDAG_links.txt"
    zplFile = "/tmp/LinksToDAG_links.zpl"    
    solutionFile = "/tmp/LinksToDAG_solutions.txt"
    linksConllFile = "LinksToDAG_links.conll"
    open(linksFile, 'w+').close()
    open(zplFile, 'w+').close()
    open(solutionFile, 'w+').close()
    open(linksConllFile, 'w+').close()

    """parser = argparse.ArgumentParser(description='Link Edge to DAG Solver.')
    parser.add_argument("--dot", dest="dot", default=False, action="store_true",
                        help="Outputs the solution in .dot format.")
    parser.add_argument("--conll", dest="conll", default=True, action="store_true",
                        help="Outputs the solution in .conll format.")
    
    parser.add_argument("strings",nargs="*")

    args = parser.parse_args()
    """

    # Link Edge Encoder
    lines = readInput()
    (sentences, processedSentences, links) = getBatchDataFromLinkParses(lines)

    wordTags = []
    linkLabels = []
    for i in xrange(len(sentences)):
        wordTags.append(getWordTags(processedSentences[i]))
        linkLabels.append(getLinkLabelMap(links[i]))
        linksTXT(links[i],linksFile, i)


    ZimplProgram(zplFile, linksFile)    
    solutionFile = SCIP(zplFile, solutionFile)

    """
    print "SOLUTION FILE:"
    print solutionFile
    call(["cat", solutionFile])
    print
    """

    f = open(linksConllFile, 'a')

    linkDeps = decodeSCIPsolution(links,solutionFile)
    
    for i in linkDeps:
        sentence = sentences[i]
        linkDep = linkDeps[i]
        linkLabel = linkLabels[i]
        wordTag = wordTags[i]

        # Link Edge Decoder
        #linkDep = getLinkDependencies(links, linkDir)

        output = conllOutput(sentence,wordTag,linkDep,linkLabel)
        #dotOutput(sentence,wordTag,linkDep,linkLabel)
        
        f.write(output)
        
    f.close()
