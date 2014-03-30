#!/usr/bin/env python

from linkEdgeEncoder import *
from linkEdgeSolver import *
from linkEdgeDecoder import *
import argparse, sys


if __name__=="__main__":
    linksFile = "/tmp/LinksToDAG_links.txt"
    corpusSizeFile = "/tmp/LinksToDAG_corpusSize.txt"
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
    (processedSentences, links) = getBatchDataFromLinkParses(lines)
    (sentences,sizeOfCorpus) = getSentencesFromProcessedSentences(processedSentences)
    
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

    f = open(linksConllFile, 'a')

    (linkDeps, allowedLabels) = decodeSCIPsolution(links,solutionFile, True)
    
    # print out the allowed labels list to standard error. Something nice for us to have.
    allowedLabels.sort()
    for allowedLabel in allowedLabels:
        print >> sys.stderr, '{0:5} {1:5}'.format(allowedLabel[0], allowedLabel[1])
    print >> sys.stderr


    for i in linkDeps:
        sentence = sentences[i]
        linkDep = linkDeps[i]
        linkLabel = linkLabels[i]
        wordTag = wordTags[i]

        # Link Edge Decoder
        #linkDep = getLinkDependencies(links, linkDir)

        output = conllOutput(sentence,wordTag,linkDep,linkLabel)
        dotOutput(sentence,wordTag,linkDep,linkLabel)
        
        f.write(output)
        
    f.close()
