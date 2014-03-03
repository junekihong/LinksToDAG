#!/usr/bin/env python

from utils import readInput
from linklabel_table import *
from pprint import pprint
from subprocess import call
import re

# Gives the links and the sentenec from a single link parse.
def getDataFromLinkParse(lines):
    #data format: (index1, index2, layer, label)
    links = []

    # get rid of the beginning statements
    i = 0
    while True:
        line = lines[i].split()
        if line[0] == "linkparser>":
            break
        i = i + 1
    lines = lines[i:]

    sentence = ""
    processedSentence = []
    pSentFlag = False
    linkFlag = False

    for line in lines:
        if not line:
            break
            
        # extract the original sentence
        if line.find("linkparser>") == 0:
            sentence = (line[len("linkparser>"):]).strip()

        # extract out the processed sentence
        elif line.find("[(LEFT-WALL)") == 0:
            if line.rfind("]") == len(line)-1:
                processedSentence.extend(line[2:-2].split(")("))
                linkFlag = True
            elif line.rfind(")") == len(line)-1:
                processedSentence.extend(line[2:-1].split(")("))
                pSentFlag = True

        # continue extracting the processed sentence if it continues on the next line
        elif pSentFlag:
            if line.rfind("]") == len(line)-1:
                processedSentence.extend(line[1:-2].split(")("))
                pSentFlag = False
                linkFlag = True
            elif line.rfind(")") == len(line)-1:
                processedSentence.extend(line[1:-1].split(")("))
                pSentFlag = True

        # extract the links
        elif linkFlag:
            links.extend(line.split("]["))

    # I got rid of the last link item. It is always "[0]" and I don't know what its for.
    links = links[:-1]
    
    # clean up the '[' and ']' artifacts in the links. And store it as a list.
    for i in xrange(len(links)):
        links[i] = links[i].strip("[]").split()
        links[i][3] = links[i][3].strip("()")
        
    return (sentence, processedSentence, links)


# extract out the link-parser tag for each word in the sentence. 
# We'll stick it into the conll output later in the CPOS field
def getWordTags(processedSentence):    
    wordTag = {}
    i = 0
    for i in xrange(len(processedSentence)):
        index = processedSentence[i].rfind(".")
        if index != -1:
            word = processedSentence[i][:index]
            tag = processedSentence[i][index+1:]
            wordTag[word] = tag
    return wordTag


def getLinkLabelMap(links):
    linkLabel = {}
    for link in links:
        arg1 = link[0]
        arg2 = link[1]
        #layer = link[2]
        label = link[3]
        linkLabel[(arg1,arg2)] = label
        linkLabel[(arg2,arg1)] = label
    return linkLabel


def getLinkDirections_naive(links):
    linkDir = {}
    
    child = None
    parent= None
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
    directory = "/tmp/dot_"+ID
    dotFile = directory+".dot"
    
    f = open(dotFile,'w')
    f.write("digraph "+ID+" {\n")
    
    for child in linkDep:
        parents = linkDep[child]

        for parent in parents:
            f.write("\t" + str(parent) + " -> " + str(child))
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
    lines = readInput()
    (sentence, processedSentence, links) = getDataFromLinkParse(lines)

    wordTag = getWordTags(processedSentence)
    linkLabel = getLinkLabelMap(links)
    linkDir = getLinkDirections_naive(links)
    linkDep = getLinkDependencies(links, linkDir)

    conllOutput(sentence,wordTag,linkDep,linkLabel)
    dotOutput(sentence,wordTag,linkDep,linkLabel)
