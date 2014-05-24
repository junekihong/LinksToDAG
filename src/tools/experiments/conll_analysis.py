#!/usr/bin/python

import sys, os
from pprint import pprint
from tikz_dependency import *
from dependency_graph import *
from conll_analysis_output import *

CONLL_DIR = "data/"
CONLL_LOC = CONLL_DIR+"english_bnews_train.conll"
if len(sys.argv) > 2:
    CONLL_LOC = sys.argv[2]
if not os.path.exists(CONLL_DIR):
    os.makedirs(CONLL_DIR)

SOL_DIR = "sol/"
SOL_LOC = SOL_DIR+"links.conll"
if not os.path.exists(SOL_DIR):
    os.makedirs(SOL_DIR)

ANALYSIS_DIR = "sol/conll_analysis/"
ANALYSIS_FILE = ANALYSIS_DIR+"conll_analysis.txt"
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)

TIKZ_DIR = "doc/figure/"
TIKZ_LOC = TIKZ_DIR+"sentences.tikz"
if not os.path.exists(TIKZ_DIR):
    os.makedirs(TIKZ_DIR)
TIKZ = open(TIKZ_LOC, 'w+')

ALL_PARSES_LOC = TIKZ_DIR+"allparses.tikz"
ALL_PARSES = open(ALL_PARSES_LOC, 'w+')


# Analysis
def analysis(conlls, links):

    word_data = analysis_words(conlls, links)
    
    graph_conlls = getGraph(conlls)
    graph_links = getGraph(links)

    matches = []
    reverse_matches = []
    extras = []

    label_match = {}
    label_match_count = {}

    label_reverse = {}
    label_reverse_count = {}

    label_extra = {}
    label_extra_count = {}
    
    mismatches = 0
    blanks = 0
    total = 0
    
    for head in graph_conlls.table:
        children = graph_conlls.table[head]
        total += len(children)

        for child in children:
            conll_label = graph_conlls.getEdge(head,child)

            # If we have a match
            if graph_links.existsEdge(head,child):
                matches.append((head,child))
                link_label = graph_links.getEdge(head,child)
                
                label_match[conll_label] = label_match.get(conll_label, set([])).union(set([link_label]))
                label_match_count[(conll_label, link_label)] = label_match_count.get((conll_label, link_label),0) + 1

            # If we have a reverse match
            elif graph_links.existsEdge(child,head):
                reverse_matches.append((child,head))
                link_label = graph_links.getEdge(child,head)
                
                label_reverse[conll_label] = label_reverse.get(conll_label, set([])).union(set([link_label]))
                label_reverse_count[(conll_label, link_label)] = label_reverse_count.get((conll_label, link_label), 0) + 1

            # We have a mismatch
            else:
                mismatches += 1
                if not graph_links.heads.get(child,[]):
                    blanks +=1

    # Delete the matches from the graphs, so we can work with the rest
    for match in matches:
        (head,child) = match
        graph_conlls.deleteEdge(head,child)
        graph_links.deleteEdge(head,child)

    # Delete the reverse matches from the graphs, so wecan work with the rest
    for reverse in reverse_matches:
        (child,head) = reverse
        graph_conlls.deleteEdge(head,child)
        graph_links.deleteEdge(child,head)
    
    # Find the extra links
    for head in graph_links.table:
        children = graph_links.table[head]
        
        for child in children:
            if len(graph_links.heads[child]) > 1:
                extras.append((head,child))
                link_label = graph_links.getEdge(head,child)

                label_extra[link_label] = label_extra.get(link_label, set([])).union(set([link_label]))
                label_extra_count[link_label] = label_extra_count.get(link_label,0) + 1

    # Delete the extras from link graph, so we can work with the rest
    for extra in extras:
        (head, child) = extra
        graph_links.deleteEdge(head,child)

    matches = len(matches)
    reverse_matches = len(reverse_matches)
    extras = len(extras)

    match_data = (matches, label_match, label_match_count)
    reverse_data = (reverse_matches, label_reverse, label_reverse_count)    
    extra_data = (extras, label_extra, label_extra_count)
    mismatch_data = (mismatches, blanks)

    return (match_data, reverse_data, extra_data, word_data, mismatch_data, total)


# Counts the word tokens that are multiheaded or dropped. Compared with the total number of word tokens
def analysis_words(conlls,links):
    word_count = 0

    dropped_word_count = 0    
    multiheaded_count = 0
    isMultiheaded = False
    hasDropped = False
    
    word_count += len(links)
    
    for conll,link in zip(conlls,links):
        link = link.split()
        
        if link[6] == "-":
            dropped_word_count += 1
            hasDropped = True

        link_heads = link[6].split(",")

        if len(link_heads) > 1:
            multiheaded_count += 1
            isMultiheaded = True


    return (dropped_word_count, multiheaded_count, word_count, hasDropped, isMultiheaded)






# The result maps will map a sentence to its conll representation.
# We will use this to query conll results from both our conll and link-conll files
conll_results = {}
link_results = {}
matching_sentences = []


# Populating the conll_results and link_results
f = open(CONLL_LOC)
f = f.readlines()
sentence = []
conll = []

for line in f:
    line = line.strip()

    if not line:
        # The sentence is stored as lower case, because link-parser will sometimes lowercase the words that it does not know.
        ID = " ".join(sentence)
        ID = ID.lower()

        conll_results[ID] = tuple(conll)
        sentence = []
        conll = []
    else:

        conll.append(line)
        word = line.split()[1]
        sentence.append(word)

# Populating the link_results
f = open(SOL_LOC)
f = f.readlines()
sentence = []
conll = []
for line in f:
    line = line.strip()
#print line

    if not line:
        # The sentence is stored as lower case.
        ID = " ".join(sentence)
        ID = ID.lower()
        link_results[ID] = tuple(conll)
        sentence = []
        conll = []
    else:
        conll.append(line)
        word = line.split()[1]

        # Remove the [!] at the end of words that link parser could not recognize
        index = -1
        index = word.rfind("[!]")
        if index != -1:
            word = word[:(index)]

        # Get rid of the [] brackets around words that the link-parser could not attach.        
        word = word.strip("[]")
        sentence.append(word)






final_total = 0

match_total = 0
all_matches = {}
all_match_counts = {}

extra_total = 0
all_extra_counts = {}

blank_total = 0
all_blank_counts = {}

mismatch_total = 0
reverse_match_total = 0
mismatch_directionality = {}
mismatch_directionality_counts = {}

#mismatch_extra_total = 0
#mismatch_extra_counts = {}



multiheaded_word_count = 0
dropped_word_total = 0
word_count_total = 0

multiheaded_sentence_count = 0
dropped_sentence_count = 0
total_sentence_count = len(link_results)


sentenceCount = 0
skip_sentenceCount = 4

allParseCount = 0
tikzCount = 4

for linkSentence in link_results:
    if linkSentence in conll_results:
        matching_sentences.append(linkSentence)

        if sentenceCount < tikzCount and len(linkSentence.split()) > 4 and len(linkSentence.split()) < 7:
            if skip_sentenceCount > 0:
                skip_sentenceCount -= 1
            else:
                tikz = tikz_dependency(conll_results[linkSentence], link_results[linkSentence], linkSentence, .9 / 2)            
                TIKZ.write(tikz)
                sentenceCount += 1
                if sentenceCount % 2 == 0:
                    TIKZ.write("\n")

        tikz = tikz_dependency(conll_results[linkSentence], link_results[linkSentence], linkSentence, 1.0, False)
        ALL_PARSES.write("\\begin{figure*}[ht!]\n")
        ALL_PARSES.write(tikz)
        ALL_PARSES.write("\\end{figure*}\n\n")
        allParseCount += 1
        if allParseCount % 3 == 0:
            ALL_PARSES.write("\clearpage")


        (match_data, reverse_data, extra_data, word_data, mismatch_data, total) = analysis(conll_results[linkSentence], link_results[linkSentence])

        (matches, label_match, label_match_count)                           = match_data
        (reverse_matches, label_reverse, label_reverse_count)               = reverse_data
        (extras, label_extra, label_extra_count)                            = extra_data
        (dropped_word_count, multiheaded_count, word_count, hasDropped, isMultiheaded)                      = word_data
        (mismatches, blanks)                                                = mismatch_data 


        match_total += matches
        blank_total += blanks
        reverse_match_total += reverse_matches
        mismatch_total += mismatches

        extra_total += extras
        final_total += total

        multiheaded_word_count += multiheaded_count
        dropped_word_total += dropped_word_count
        word_count_total += word_count


        if isMultiheaded:
            multiheaded_sentence_count += 1 

        if hasDropped:
            dropped_sentence_count += 1

        for label in label_match:
            all_matches[label] = all_matches.get(label,set([])).union(label_match[label])
        for pair in label_match_count:
            all_match_counts[pair] = all_match_counts.get(pair,0) + label_match_count[pair]

        for label in label_extra_count:
            all_extra_counts[label] = all_extra_counts.get(label, 0) + label_extra_count[label]

        for label in label_reverse:
            mismatch_directionality[label] = mismatch_directionality.get(label, set([])).union(label_reverse[label])

        for pair in label_reverse_count:
            mismatch_directionality_counts[pair] = mismatch_directionality_counts.get(pair,0) + label_reverse_count[pair]



result = result_numbers(final_total, 
                        match_total, 
                        extra_total, 
                        blank_total, 
                        mismatch_total, 
                        reverse_match_total, 
                        #mismatch_extra_total, 
                        dropped_word_total,
                        multiheaded_word_count, 
                        word_count_total, 
                        dropped_sentence_count,
                        multiheaded_sentence_count, 
                        total_sentence_count)



f = open(ANALYSIS_FILE, "w+")
f.write(result)
f.close()







print result
