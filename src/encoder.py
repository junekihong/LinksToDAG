#!/usr/bin/env python

from tools.utils import readInput
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

        
        # extract the original sentence. Populate the corpus.
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
        
    return (processedSentence, links)


# Gives all the links and the sentences from a given wholesale batch link parse.
def getBatchDataFromLinkParses(lines):
    #sentences = []
    processedSentences = []
    linkData = []
    
    i = 0
    for j in xrange(len(lines)):
        if not lines[j]:
            singleParse = lines[i:j]
            (processedSentence, links) = getDataFromLinkParse(singleParse)
            
            #sentences.append(sentence)
            processedSentences.append(processedSentence)
            linkData.append(links)
            i = j+1
    return (processedSentences, linkData)


# Gets the original sentence from the processed sentence.
# Because of how link-parser outputs its links, it is not necessarily aligned with the original sentence.
# We also calculate the size of the corpus here.
def getSentencesFromProcessedSentences(processedSentences):
    sentences = []    
    corpus = {}
    for processed in processedSentences:
        # Get rid of LEFT-WALL
        processed = processed[1:]
        
        for i in xrange(len(processed)):
            if processed[i][0] == "[" and processed[i][-1] == "]":
                continue
            index = processed[i].rfind(".")
            
            if index != -1:
                processed[i] = processed[i][:index]
                index = processed[i].rfind("[")
                index2 = processed[i].rfind("]")
                if index != -1 and index2 != -1 and index2 > index:
                    processed[i] = processed[i][:index]

        sentence =" ".join(processed)
        sentences.append(sentence)
        
        # Add the unique words to the corpus
        for word in sentence.split():
            corpus[word] = True

    sizeOfCorpus = len(corpus)
    return (sentences, sizeOfCorpus)


# extract out the link-parser tag for each word in the sentence. 
# We'll stick it into the conll output later in the CPOS field
def getWordTags(processedSentence):
    wordTag = {}
    i = 0
    for i in xrange(len(processedSentence)):
        if processedSentence[i][0] == "[" and processedSentence[i][-1] == "]":
            continue

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
def linksTXT(links, filename = "/tmp/LinksToDAG_links.txt", index = 0):
    index = str(index)
    DELIMITER = "#"
    f = open(filename, 'a')

    #data format: (index1, index2, layer, label)    
    for link in links:
        node1 = link[0]
        node2 = link[1]
        layer = link[2]
        label = link[3]
        
        string = ""
        #string = name+", "+
        string += node1+", "+node2+", "+layer+", "+label+", "+index+"\n"
        
        f.write(string)
    f.close()


# Produce the Zimpl Program to solve
def ZimplProgram(zplFilename, linkFilename, corpusSize):
    f = open(zplFilename, 'w')
    keyword = {}
    keyword["$LINKFILENAME$"] = linkFilename
    keyword["$CORPUSSIZE$"] = str(corpusSize)

    # Read in our Zimpl file template
    z = open("src/zimpl_template.zpl",'r')
    z = z.readlines()
    for line in z:
        for key in keyword:
            line = line.replace(key,keyword[key])
        #print line
        f.write(line)

    f.close()


if __name__=="__main__":
    linksFile = "/tmp/LinksToDAG_links.txt"
    zplFile = "/tmp/LinksToDAG_links.zpl"    


    # Link Edge Encoder
    lines = readInput()

    (processedSentence, links) = getBatchDataFromLinkParses(lines)
    (sentences,sizeOfCorpus) = getSentencesFromProcessedSentences(processedSentence)
    
    #print "sentences:"
    #pprint(sentences)
    
    for i in xrange(len(sentences)):
        #print sentences[i]
        #pprint(processedSentence[i])
        #pprint(links[i])

        wordTag = getWordTags(processedSentence[i])
        linkLabel = getLinkLabelMap(links[i])
        linksTXT(links[i], linksFile, i)

        #pprint(wordTag)
        #pprint(linkLabel)
        

    ZimplProgram(zplFile, linksFile, sizeOfCorpus)
