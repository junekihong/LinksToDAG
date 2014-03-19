#!/usr/bin/env python

from linkEdgeEncoder import *
from linkEdgeSolver import *
from subprocess import call
import re
from pprint import pprint


# Given a list of all the links for each sentence and a solution file, we decode the solution.
def decodeSCIPsolution(links, solutionFile):
    linkDeps = {}

    f = open(solutionFile, 'r')
    lines = f.readlines()
    
    decodedSolutions = {}


    for line in lines:
        if line.find("direction#") != -1:
            line = line.split()
            ID = line[0]
            direction = int(line[1])


            ID = ID.split("#")[1:]
            layer_label = ID[2].split("$")
            node1 = ID[0]
            node2 = ID[1]
            layer = layer_label[0]
            label = layer_label[1]
            sentence = int(ID[3])
            
            if decodedSolutions.get(sentence, None) == None:
                decodedSolutions[sentence] = [(node1,node2,layer,label,direction)]
            else:
                decodedSolutions[sentence].append((node1,node2,layer,label,direction))
            
    for sentence in decodedSolutions:
        linkDep = {}
        processedLinks = decodedSolutions[sentence]
        originalLinks = links[sentence]
        
        for link in processedLinks:
            node1 = link[0]
            node2 = link[1]
            layer = link[2]
            label = link[3]
            direction = link[4]
            # TODO
            # The output of SCIP does not print out the direction variables that are 0.
            # I suspect there are settings in SCIP that will not suppress these variables
            # But for now, my solution is to find the remaining links that were not outputted by SCIP, because those are the ones set to 0.
            # So this is why I remove those links.
            originalLinks = [x for x in originalLinks if x[0] != node1 or x[1] != node2 or x[2] != layer or x[3] != label]
            
            # direction right
            """if direction == 0:
                parent = node2
                child = node1
            """
            # direction left
            #elif
            if direction == 1:
                parent = node1
                child = node2

            if child in linkDep.keys():
                linkDep[child].append(parent)
            else:
                linkDep[child] = [parent]

        # The rest of the links that remain have direction right
        for link in originalLinks:
            node1 = link[0]
            node2 = link[1]
            layer = link[2]
            label = link[3]
            
            parent = node2
            child = node1
            if child in linkDep.keys():
                linkDep[child].append(parent)
            else:
                linkDep[child] = [parent]
        linkDeps[sentence] = linkDep

    return linkDeps

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
    """
    # output this to a temp file. Strip out the non alphanumeric characters
    ID = "".join(sentence.split(" "))
    ID = re.sub(r'\W+', '', ID)
    ID = ID[:30]
    
    directory = "/tmp/LinksToDAG_conll_"+ID
    linkFile = directory+".link"
    f = open(linkFile,'w')
    """
    output = ""

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


        CONLL_LINE= "\t".join([str(i), word, LEMMA, CPOS, POS, FEATS, parents, labels])
        #print CONLL_LINE
        #f.write(CONLL_LINE+"\n")
        output += CONLL_LINE+"\n"
        i = i+1

    #print
    output += "\n"
    #f.close()
    return output
    

def dotOutput(sentence, wordTag, linkDep, linkLabel):

    # output this to a temp file. Strip out the non alphanumeric characters
    ID = "".join(sentence.split(" "))
    ID = re.sub(r'\W+', '', ID)
    ID = ID[:30]
    sentence = sentence.split()
    

    directory = "/tmp/LinksToDAG_dot_"+ID
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
    linkDep = decodeSCIPsolution(links,solutionFile)

    #pprint(linkLabel)
    
    # Link Edge Decoder
    #linkDep = getLinkDependencies(links, linkDir)
    conllOutput(sentence,wordTag,linkDep,linkLabel)
    dotOutput(sentence,wordTag,linkDep,linkLabel)
    
