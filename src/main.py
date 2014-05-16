#!/usr/bin/env python

from encoder import *
from solver import *
from decoder import *
from tools.cache import *
import argparse, sys


if __name__=="__main__":
    cache = cache("/tmp/LinksToDAG_SCIP_cache.p")


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


    # Argument parser. To support command line flags
    parser = argparse.ArgumentParser(description="Runs the LinksToDAG project")
    parser.add_argument("-id", "--ID", dest="ID", default=None,
                       help="Set the ID, this is used to cache results")
    #parser.add_argument("-lang","--language", dest="language", default="en"
    #                    help="Set the language that we will parse in")
    parser.add_argument("strings", nargs="*")
    args = parser.parse_args()



    # TODO
    # already in the cache
    if args.ID != None and cache.check(args.ID):
        print "SCIP SOLUTION FOUND IN CACHE"
        (sentences, linkLabels, wordTags, allowedLabels, linkDeps) = cache.get(args.ID)
    else:            
        lines = []
        for filename in args.strings:
            f = open(filename)
            f = f.readlines()
            for line in f:
                line = line.strip()
                lines.append(line)


        # Link Edge Encoder
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

        (linkDeps, allowedLabels) = decodeSCIPsolution(links,solutionFile, True)
        
        allowedLabels.sort()
        cache.store(args.ID, (sentences, linkLabels, wordTags, allowedLabels, linkDeps))



    # Save the allowed links solution file.
    open(allowedLinksFile, 'w+').close()
    allowedLinks = open(allowedLinksFile, 'w')
    for allowedLabel in allowedLabels:
        allowedLinks.write('{0:5} {1:5}\n'.format(allowedLabel[0], allowedLabel[1]))
    
    allowedLinks.write("\n")
    allowedLinks.close()

    # Save the links conll solution file.
    open(linksConllFile, 'w+').close()
    linksConll = open(linksConllFile, 'w')
    for i in linkDeps:
        sentence = sentences[i]
        linkDep = linkDeps[i]
        linkLabel = linkLabels[i]
        wordTag = wordTags[i]

        output = conllOutput(sentence,wordTag,linkDep,linkLabel)
        #dotOutput(sentence,wordTag,linkDep,linkLabel)


        linksConll.write(output)
        
    linksConll.close()

    cache.save()
