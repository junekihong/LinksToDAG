#!/usr/bin/env python

from utils import readInput
from linklabel_table import *
from pprint import pprint


# Gives the links and the sentence from a single link parse.
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

# Construct a map that will retrieve any label for any given link.
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


# Produce the list of links out to a file
def linksTXT(links, filename = "/tmp/links.txt"):
    f = open(filename, 'w')

    #data format: (index1, index2, layer, label)    
    for link in links:
        node1 = link[0]
        node2 = link[1]
        layer = link[2]
        label = link[3]
        
        DELIMITER = "#"
        name = node1+DELIMITER+node2+DELIMITER+layer+DELIMITER+label
        f.write(name+", "+node1+", "+node2+", "+layer+", "+label+"\n")
    f.close()


# Produce the Zimpl Program to solve
def ZimplProgram(zplFilename, linkFilename):
    f = open(zplFilename, 'w')
    header = "# Link Edge to DAG Zimpl file.\n# Juneki Hong\n\n"
    divider = "\n# ----------\n\n"

    f.write(header)
    f.write(divider)
    
    readInData = "# Read in the data. (ID, node1, node2, layer, label)\n"
    readInData += "set DATA := { read \""+linkFilename+"\" as \"<1s, 2n, 3n, 4n, 5s>\" };\n"
    readInData += "set ID := proj(DATA, <1>);\n"
    readInData += "set I := proj(DATA, <2>);\n"
    readInData += "set J := proj(DATA, <3>);\n"
    readInData += "set E := { <i,j> in I*J with i<j };\n"

    f.write(readInData)
    f.write(divider)
    
    linkData = "# Link data.\n"
    linkData += "set IJ := proj(DATA, <2,3>);\n"
    #linkData += "param link[<i,j> in IJ] := 1;\n"
    linkData += "param link[<i,j> in E] := 1;\n"

    f.write(linkData)
    f.write(divider)

    variables = "# Variables.\n"
    variables += "var direction[ID] binary;\n"
    f.write(variables)
    f.write(divider)


    linkDescriptions = "# Link descriptions\n"
    linkDescriptions = ""
    #linkDescriptions += "var llink[<i,j> in IJ] := link[<i,j>];\n"
    linkDescriptions += "\n"

    f.write(linkDescriptions)
    f.write(divider)


    tempObjective = "# Objective.\n"

    tempObjective = tempObjective+"minimize cycles : sum<id> in ID : -direction[id];\n"
    tempObjective += "subto constraint : sum <id,i,j,layer,label> in DATA : (j-i)*direction[id] <= 5;\n"


    f.write(tempObjective)
    f.write(divider)
    f.close()


if __name__=="__main__":
    # Link Edge Encoder
    lines = readInput()
    (sentence, processedSentence, links) = getDataFromLinkParse(lines)

    wordTag = getWordTags(processedSentence)
    linkLabel = getLinkLabelMap(links)

    linksFile = "/tmp/links.txt"
    linksTXT(links,linksFile)

    zplFile = "/tmp/links.zpl"
    ZimplProgram(zplFile, linksFile)


    
