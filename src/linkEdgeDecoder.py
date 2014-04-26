#!/usr/bin/env python

from linkEdgeEncoder import *
from linkEdgeSolver import *
from subprocess import call
import re
from pprint import pprint
import os


# Given a list of all the links for each sentence and a solution file, we decode the solution.
def decodeSCIPsolution(links, solutionFile, getAllowedLabels=False):
    linkDeps = {}
    allowedLabels = []
    
    f = open(solutionFile, 'r')
    lines = f.readlines()
    
    decodedSolutions = {}


    for line in lines:
        if line.find("rlink#") == 0:
            line = line.split()
            ID = line[0]
            direction = int(round(float(line[1])))

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

        elif line.find("allowedLabel$") == 0:
            #print line

            line = line.split()
            ID = line[0]
            variableValue = int(round(float(line[1])))
            
            if variableValue == 1:
                ID = ID.split("$")[1]
                ID = ID.split("#")
                label = ID[0]
                direction = ID[1]
                allowedLabels.append((label,direction))

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
            
            # direction left
            if direction == 0:
                parent = node2
                child = node1
            
            # direction right
            elif direction == 1:
                parent = node1
                child = node2

            if child in linkDep.keys():
                linkDep[child].append(parent)
            else:
                linkDep[child] = [parent]

        # The rest of the links that remain
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


    if getAllowedLabels:
        return (linkDeps, allowedLabels)
    else:
        return (linkDeps)

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
    BLANK = "-"
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
            parents = BLANK
        if not labels:
            labels = BLANK

        #print "children",children
        #print "labels",labels
        
        word = sentence[i-1]
        LEMMA = BLANK
        CPOS = BLANK
        POS = BLANK
        if word in wordTag.keys():
            CPOS = wordTag[word]
        FEATS = BLANK
        
        VPARENTS = BLANK
        VLABELS = BLANK

        CONLL_LINE= "\t".join([str(i), word, LEMMA, CPOS, POS, FEATS, parents, labels, VPARENTS, VLABELS])
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
    

    directory = "/tmp/LinksToDAG_dot/"
    # If needed, make the directory to put all of our dot files. 
    if not os.path.exists(directory):
        os.makedirs(directory)

    File = directory+"LinksToDAG_dot_"+ID
    dotFile = File+".dot"    
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
    pngFile = File+".png"
    f = open(pngFile,'w')
    call(["dot","-Tpng",dotFile],stdout=f)
    f.close()



if __name__=="__main__":
    solutionFile = "/tmp/LinksToDAG_solutions.txt"
    linksConllFile = "LinksToDAG_links.conll"
    open(solutionFile, 'w+').close()
    open(linksConllFile, 'w+').close()

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
