#!/usr/bin/env python

from linkEdgeEncoder import *
from linkEdgeSolver import *
from linkEdgeDecoder import *
import argparse

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='Link Edge to DAG Solver.')
    parser.add_argument("--dot", dest="dot", default=False, action="store_true",
                        help="Outputs the solution in .dot format.")
    parser.add_argument("--conll", dest="conll", default=True, action="store_true",
                        help="Outputs the solution in .conll format.")
    
    parser.add_argument("strings",nargs="*")

    args = parser.parse_args()


    # Link Edge Encoder
    lines = readInput()
    (sentence, processedSentence, links) = getDataFromLinkParse(lines)
    
    wordTag = getWordTags(processedSentence)
    linkLabel = getLinkLabelMap(links)
    
    # Link Edge Solver
    linkDir = getLinkDirections_naive(links)

    # Link Edge Decoder
    linkDep = getLinkDependencies(links, linkDir)
    conllOutput(sentence,wordTag,linkDep,linkLabel)
    dotOutput(sentence,wordTag,linkDep,linkLabel)
    
        
