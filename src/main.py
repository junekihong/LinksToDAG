#!/usr/bin/env python

from encoder import *
from solver import *
from decoder import *
import argparse, sys


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


    open(linksConllFile, 'w+').close()
    f = open(linksConllFile, 'a')

    (linkDeps, allowedLabels) = decodeSCIPsolution(links,solutionFile, True)
    
    # print out the allowed labels list to standard error. Something nice for us to have.
    allowedLabels.sort()


    open(allowedLinksFile, 'w+').close()
    allowedLinks = open(allowedLinksFile, 'w')
    for allowedLabel in allowedLabels:
        allowedLinks.write('{0:5} {1:5}\n'.format(allowedLabel[0], allowedLabel[1]))
    
    allowedLinks.write("\n")
    allowedLinks.close()

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

