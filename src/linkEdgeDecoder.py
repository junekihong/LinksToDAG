#!/usr/bin/env python

from linkEdgeEncoder import *
from linkEdgeSolver import *
from subprocess import call
import re
from pprint import pprint


def decodeSCIPsolution(solutionFile):
    linkDep = {}
    f = open(solutionFile, 'r')
    lines = f.readlines()
    
    for line in lines:
        if line.find("direction$") != -1:
            line = line.split()
            ID = line[0]
            direction = int(line[1])
            
            ID = ID.split("$")[1].split("#")
            node1 = ID[0]
            node2 = ID[1]
            #layer = int(ID[2])
            #label = ID[3]

            # direction right
            if direction == 0:
                parent = node2
                child = node1
            # direction left
            elif direction == 1:
                parent = node1
                child = node2


            if child in linkDep.keys():
                linkDep[child].append(parent)
            else:
                linkDep[child] = [parent]
    return linkDep

# Construct a link dependency map, given that we have already solved all the directionality assignments.
def getLinkDependencies(links, linkDir):
    linkDep = {}
    for link in links:
        node1 = link[0]
        node2 = link[1]
        level = link[2]
        label = link[3]
        direction = linkDir[tuple(link)]

        # direction left
        if direction == True:
            parent = node2
            child = node1
        # direction right
        elif direction == False:
            parent = node1
            child = node2
        
        if child in linkDep.keys():
            linkDep[child].append(parent)
        else:
            linkDep[child] = [parent]
    return linkDep


def conllOutput(sentence, wordTag, linkDep, linkLabel):
    sentence = sentence.split()
    i = 1
    while i < len(sentence)+1:
        parents = []
        if str(i) in linkDep.keys():
            parents = linkDep[str(i)]
        labels = []
        for parent in parents:
            labels.append(linkLabel[(str(i),parent)])
        parents = ",".join(parents)
        labels = ",".join(labels)

        if not parents:
            parents = "_"
        if not labels:
            labels = "_"

        #print "children",children
        #print "labels",labels
        
        word = sentence[i-1]
        LEMMA = "_"
        CPOS = "_"
        POS = "_"
        if word in wordTag.keys():
            CPOS = wordTag[word]
        FEATS = "_"


        print "\t".join([str(i), word, LEMMA, CPOS, POS, FEATS, parents, labels])
        i = i+1

    print
    

def dotOutput(sentence, wordTag, linkDep, linkLabel):

    # output this to a temp file. Strip out the non alphanumeric characters
    ID = "".join(sentence.split(" "))
    ID = re.sub(r'\W+', '', ID)
    ID = ID[:30]
    sentence = sentence.split()
    

    directory = "/tmp/dot_"+ID
    dotFile = directory+".dot"
    
    f = open(dotFile,'w')
    f.write("digraph "+ID+" {\n")

    for child in linkDep:
        parents = linkDep[child]

        for parent in parents:
            if int(parent) == 0:
                parentString = "ROOT"
            else:
                parentString = re.sub(r'\W+','', sentence[int(parent)-1])

            if int(child) == 0:
                childString = "ROOT"
            else:
                childString = re.sub(r'\W+','', sentence[int(child)-1])
            

            relationship = "\t" + parentString+str(int(parent))
            relationship = relationship + " -> " + childString+str(int(child))
            
            f.write(relationship)
            f.write(" [ label=")
            f.write(re.sub(r'\W+','_', linkLabel[(child,parent)]))
            f.write("]")
            f.write("\n")
    f.write("}\n")
    f.close()

    # call dot on the temp file. Store the image.
    pngFile = directory+".png"
    f = open(pngFile,'w')
    call(["dot","-Tpng",dotFile],stdout=f)
    f.close()



if __name__=="__main__":
    # Link Edge Encoder
    lines = readInput()
    (sentence, processedSentence, links) = getDataFromLinkParse(lines)

    wordTag = getWordTags(processedSentence)
    linkLabel = getLinkLabelMap(links)

    # Link Edge Solver
    #linkDir = getLinkDirections_naive(links)
    
    linksFile = "/tmp/links.txt"
    linksTXT(links,linksFile)
    
    zplFile = "/tmp/links.zpl"
    ZimplProgram(zplFile, linksFile)
    
    solutionFile = SCIP(zplFile)
    linkDep = decodeSCIPsolution(solutionFile)


    # Link Edge Decoder
    #linkDep = getLinkDependencies(links, linkDir)
    conllOutput(sentence,wordTag,linkDep,linkLabel)
    dotOutput(sentence,wordTag,linkDep,linkLabel)
    
