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




# Gives all the links and the sentences from a given wholesale batch link parse.
def getBatchDataFromLinkParses(lines):
    sentences = []
    processedSentences = []
    linkData = []
    
    i = 0
    for j in xrange(len(lines)):
        if not lines[j]:
            singleParse = lines[i:j]
            (sentence, processedSentence, links) = getDataFromLinkParse(singleParse)
            
            sentences.append(sentence)
            processedSentences.append(processedSentence)
            linkData.append(links)
            i = j+1
    return (sentences, processedSentences, linkData)


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
def linksTXT(links, filename = "/tmp/links.txt", index = 0):
    index = str(index)
    DELIMITER = "#"
    f = open(filename, 'a')

    #data format: (index1, index2, layer, label)    
    for link in links:
        node1 = link[0]
        node2 = link[1]
        layer = link[2]
        label = link[3]
        
        # The name is all of the data and an index combined together. 
        # The index represents which sentence this link came from. 
        # This will be used as indentification later. 
        # From the ID, we can determine any particular link from a particular sentence.
        #name = node1+DELIMITER+node2+DELIMITER+layer+DELIMITER+label+DELIMITER+index
        string = ""
        #string = name+", "+
        string += node1+", "+node2+", "+layer+", "+label+", "+index+"\n"
        
        f.write(string)
    f.close()


# Produce the Zimpl Program to solve
def ZimplProgram(zplFilename, linkFilename):
    f = open(zplFilename, 'a')
    header = "# Link Edge to DAG Zimpl file.\n# Juneki Hong\n\n"
    divider = "\n# ----------\n\n"
    f.write(header)
    f.write(divider)
    
    readInData = "# Read in the data. (node1, node2, layer, label, sentence)\n"
    readInData += "set LINK := { read \""+linkFilename+"\" as \"<1n, 2n, 3n, 4s, 5n>\" };\n"

    # Possible Labels
    readInData += "set LABELS := proj(LINK,<4>);\n"
    #readInData += "set LABELS := { read \""+linkFilename+"\" as \"<4s>\" };\n"
    readInData += "set DIRECTIONS := { 0, 1 };\n"
    readInData += "set POSSIBLE_LABELS := LABELS * DIRECTIONS;\n"

    # List of Nodes
    readInData += "set NODE1 := proj(LINK,<1,5>);\n"
    readInData += "set NODE2 := proj(LINK,<2,5>);\n"

    #readInData += "set NODE1 := { read \""+linkFilename+"\" as \"<1n, 5n>\" };\n"
    #readInData += "set NODE2 := { read \""+linkFilename+"\" as \"<2n, 5n>\" };\n"
    readInData += "set NODE := NODE1 union NODE2;\n"
    readInData += "set NODE_PAIR := { <i,sentence1,j,sentence2> in NODE * NODE with sentence1 == sentence2 and i < j };"

    
    f.write(readInData)
    f.write(divider)

    variables = "# Variables.\n"
    variables += "var direction[LINK] binary;\n"
    variables += "var allowedLabel[POSSIBLE_LABELS] binary;\n"
    variables += "var slackLabel[POSSIBLE_LABELS] binary;\n"

    variables += "var depth[NODE] >= -infinity;\n"

    variables += "\n# Left and Right links\n"
    variables += "var llink[NODE_PAIR] binary;\n"
    variables += "var rlink[NODE_PAIR] binary;\n"

    variables += "var hasParent[NODE] binary;\n"

    f.write(variables)
    f.write(divider)

    objective = "# Objective and Constraints.\n"
    objective += "\n# Minimize the number of allowed labels used.\n"
    objective += "minimize labelsUsed : sum<label, dir> in POSSIBLE_LABELS : (allowedLabel[label,dir] + 10000*slackLabel[label,dir]);\n"

    objective += "\n# Every link gets an allowed label.\n"
    objective += "subto atLeastOneLabel : forall <i,j,layer,label,sentence> in LINK : allowedLabel[label,0] + allowedLabel[label, 1] +slackLabel[label,0] + slackLabel[label,1]>= 1;\n"
    objective += "subto onlyOneAllowedLabel : forall <i,j,layer,label,sentence> in LINK : allowedLabel[label,0] == 1-allowedLabel[label,1];\n"

    objective += "\n# Set the direction variable to match the direction specified in allowedLabel\n"
    objective += "subto assignLabel_L : forall <i,j,layer,label,sentence> in LINK : sum <label, 0> in POSSIBLE_LABELS : allowedLabel[label,0]+slackLabel[label,0] >= 1 - direction[i,j,layer,label,sentence];\n"
    objective += "subto assignLabel_R : forall <i,j,layer,label,sentence> in LINK : sum <label, 1> in POSSIBLE_LABELS : allowedLabel[label,1]+slackLabel[label,1] >= direction[i,j,layer,label,sentence];\n"

    objective += "\n# Specify the left and right links.\n"
    objective += "subto assign_llink : forall <i,j,layer,label,sentence> in LINK : llink[i,sentence, j, sentence] == 1 - direction[i,j,layer,label,sentence];\n"
    objective += "subto assign_rlink : forall <i,j,layer,label,sentence> in LINK : rlink[i,sentence, j, sentence] == direction[i,j,layer,label,sentence];\n"        

    
    # Uses depth to enforce acyclicity.
    objective += "subto depth_zeroInitialization: forall <0,sentence> in NODE: depth[0,sentence] == 1;\n"
    objective += "subto depth_recursive_L: forall <i,sentence,j,sentence> in NODE_PAIR: depth[i,sentence] >= llink[i,sentence,j,sentence]*(depth[j,sentence] + 1);\n"
    objective += "subto depth_recursive_R: forall <i,sentence,j,sentence> in NODE_PAIR: depth[j,sentence] >= rlink[i,sentence,j,sentence]*(depth[i,sentence] + 1);\n"


    # The root has the smallest depth.
    #objective += "subto rootDepth_smallest : forall <i,sentence> in NODE with i > 0: depth[0,sentence]+1 <= depth[i,sentence];\n"    
    
    # Everything except root needs to have a parent    
    objective += "subto everyLinkMakesAParent : forall<i,j,layer,label,sentence> in LINK : (hasParent[i,sentence]*llink[i,sentence,j,sentence] + hasParent[j,sentence]*rlink[i,sentence,j,sentence]) == 1;\n"

    objective += "subto noLinkThenNoParent : forall<j,sentence> in NODE : hasParent[j,sentence] <= sum<i,j,layer,label,sentence> in LINK : rlink[i,sentence,j,sentence] + sum<j,k,layer2,label2,sentence> in LINK : llink[j,sentence,k,sentence] ;\n"
    


    objective += "subto everyOneHasParent : forall<i,sentence> in NODE with i > 0 : hasParent[i,sentence] == 1;\n"
    objective += "subto rootHasNoParent : forall<0,sentence> in NODE : hasParent[0,sentence] == 0;\n"


    # temporary constraint.
    #objective += "subto constraint : sum <label,1> in POSSIBLE_LABELS : allowedLabel[label,1] <= ((sum <label,dir> in POSSIBLE_LABELS: allowedLabel[label,dir]) / 1.5);\n"
    #objective += "subto constraint2 : sum <label,0> in POSSIBLE_LABELS : allowedLabel[label,0] <= ((sum <label,dir> in POSSIBLE_LABELS: allowedLabel[label,dir]) / 1.5);\n"

    f.write(objective)
    f.write(divider)
    f.close()


if __name__=="__main__":
    # Link Edge Encoder
    lines = readInput()

    (sentences, processedSentence, links) = getBatchDataFromLinkParses(lines)

    for i in xrange(len(sentences)):
        print sentences[i]
        pprint(processedSentence[i])
        pprint(links[i])


        wordTag = getWordTags(processedSentence[i])
        linkLabel = getLinkLabelMap(links[i])

        pprint(wordTag)
        pprint(linkLabel)


    """
    linksFile = "/tmp/links.txt"
    linksTXT(links,linksFile)

    zplFile = "/tmp/links.zpl"
    ZimplProgram(zplFile, linksFile)
    """
    
