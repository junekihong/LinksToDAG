#!/usr/bin/python

import sys, os
from pprint import pprint

CONLL_DIR = "data/"
SOL_DIR = "sol/"

CONLL_LOC = CONLL_DIR+"english_bnews_train.conll"
SOL_LOC = SOL_DIR+"links.conll"

if len(sys.argv) > 2:
    CONLL_LOC = sys.argv[2]

ANALYSIS_DIR = "sol/conll_analysis/"
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)
ANALYSIS_FILE = ANALYSIS_DIR+"conll_analysis.txt"



# The result maps will map a sentence to its conll representation.
# We will use this to query conll results from both our conll and link-conll files
conll_results = {}
link_results = {}

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



# Analysis on the matches.
def analysis_match(conlls, links):
    #pprint(conlls)
    #pprint(links)

    matches = 0
    extras = 0
    total = 0
    label_match = {}
    label_match_count = {}
    label_extra_count = {}

    total = len(conlls)
    for conll,link in zip(conlls, links):
        conll = conll.split()
        link = link.split()

        conll_head = conll[6]
        link_heads = link[6].split(",")
        conll_label = conll[7]
        link_labels = link[7].split(",")

        if conll_head not in link_heads:
            continue

        for head,label in zip(link_heads, link_labels):
            if head == conll_head:
                matches += 1 
                label_match[conll_label] = label_match.get(conll_label, set([])).union(set([label]))
                label_match_count[(conll_label,label)] = label_match_count.get((conll_label,label), 0) + 1
            else:
                extras += 1
                label_extra_count[label] = label_extra_count.get(label, 0) + 1

    match_data = (matches, label_match, label_match_count)
    extra_data = (extras, label_extra_count)

    return (match_data, extra_data, total)


# Analysis on the mismatches.
def analysis_mismatch(conlls, links):
    mismatches = 0

    # Directionality mismatch
    dir_miss = 0
    dir_miss_labels = {}
    dir_miss_labels_count = {}

    mismatch_extras = 0
    mismatch_extra_count = {}

    for conll,link in zip(conlls, links):
        conll = conll.split()
        link = link.split()

        index = conll[0]
        conll_head = conll[6]
        link_heads = link[6].split(",")
        conll_label = conll[7]
        link_labels = link[7].split(",")

        if conll_head not in link_heads:
            mismatches += 1
            head = int(conll[6])-1

            candidate = links[head].split()
            candidate_heads = candidate[6].split(",")
            candidate_labels = candidate[7].split(",")
            

            if index not in candidate_heads:
                continue

            dir_miss += 1

            # Iterate through the head index of the conll arc. Looking for the link pointing in the wrong direction
            for head,label in zip(candidate_heads,candidate_labels):
                if head == index:
                    dir_miss_labels[conll_label] = dir_miss_labels.get(conll_label,set([])).union(set([label]))
                    dir_miss_labels_count[(conll_label,label)] = dir_miss_labels_count.get((conll_label,label),0)+1
                    break


            for head,label in zip(link_heads, link_labels):
                mismatch_extras += 1
                mismatch_extra_count[label] = mismatch_extra_count.get(label, 0) + 1



    dir_miss_data = (dir_miss, dir_miss_labels, dir_miss_labels_count)
    mismatch_extra_data = (mismatch_extras, mismatch_extra_count)    
    mismatch_data = (mismatches, dir_miss_data, mismatch_extra_data)
    
    return mismatch_data



# All the analysis put together.
# Plus the extra links
def analysis(conlls, links):
    
    # How many links match the conll corpus
    (match_data, extra_data, total) = analysis_match(conlls, links)
    (matches, label_match, label_match_count) = match_data
    (extras, label_extra_count) = extra_data

    # Mismatch data. Including directionality mismatches
    mismatch_data = analysis_mismatch(conlls,links)
    (mismatches, dir_miss_data, mismatch_extra_data) = mismatch_data
    (dir_miss, dir_miss_labels, dir_miss_labels_count) = dir_miss_data
    (mismatch_extras, mismatch_extra_count) = mismatch_extra_data
    
    return (match_data, mismatch_data, extra_data, mismatch_extra_data, total)



match_total = 0
extra_total = 0
final_total = 0
all_matches = {}
all_match_counts = {}
all_extra_counts = {}

mismatch_total = 0
dir_mismatch_total = 0
mismatch_directionality = {}
mismatch_directionality_counts = {}

mismatch_extra_total = 0
mismatch_extra_counts = {}





for linkSentence in link_results:


    #print linkSentence.lower()
    #pprint(link_results[linkSentence])


    #print conll_results.get(linkSentence, None)

    if linkSentence in conll_results:
        
        (match_data, mismatch_data, extra_data, mismatch_extra_data, total) = analysis(conll_results[linkSentence], link_results[linkSentence])

        (matches, label_match, label_match_count) = match_data
        (extras, label_extra_count) = extra_data

        (mismatches, dir_miss_data, mismatch_extra_data) = mismatch_data
        (dir_miss, dir_miss_labels, dir_miss_labels_count) = dir_miss_data

        (mismatch_extras, mismatch_extra_count) = mismatch_extra_data


        match_total += matches
        mismatch_total += mismatches
        dir_mismatch_total += dir_miss
        mismatch_extra_total += mismatch_extras

        extra_total += extras
        final_total += total

        for label in label_match:
            all_matches[label] = all_matches.get(label,set([])).union(label_match[label])
        for pair in label_match_count:
            all_match_counts[pair] = all_match_counts.get(pair,0) + label_match_count[pair]

        for label in label_extra_count:
            all_extra_counts[label] = all_extra_counts.get(label, 0) + label_extra_count[label]
            
        for label in dir_miss_labels:
            mismatch_directionality[label] = mismatch_directionality.get(label, set([])).union(dir_miss_labels[label])

        for pair in dir_miss_labels_count:
            mismatch_directionality_counts[pair] = mismatch_directionality_counts.get(pair,0) + dir_miss_labels_count[pair]
        
        for label in mismatch_extra_count:
            mismatch_extra_counts[label] = mismatch_extra_counts.get(label,0) + mismatch_extra_count[label]



match_percent = str(0)
mismatch_percent = str(0)
if final_total != 0:
    match_percent = str(float(match_total)/final_total)
    mismatch_percent = str(float(mismatch_total)/final_total)

directional_percent = str(0)
if mismatch_total != 0:
    directional_percent = str(float(dir_mismatch_total)/mismatch_total)


result= """------------------------------------------------------------
TOTALS
------------------------------------------------------------

How many conll arcs match a link. In both attachment and directionality.
Match Total:\t\t\t\t"""+ str(match_total)+""" 
Percent of all arcs:\t\t"""+ match_percent +"""

How many links attach to a word when there is already a matching link to the conll data. How many "extra" arcs.
Extra Total:\t\t\t\t"""+str(extra_total)+"""

How many conll arcs do not match a link. In either attachment or directionality.
Mismatch Total:\t\t\t\t"""+str(mismatch_total)+"""\t
Percent of all arcs:\t\t"""+ mismatch_percent +"""

How many conll arcs do not match a link in only directionality?
Directional Mismatch Total:\t"""+str(dir_mismatch_total)+"""
Percent of all mismatches:\t"""+ directional_percent +"""

How many other links attach to a word when there is a directional mis-matching link to the conll data ?
Directional Mismatch Extra Total:\t"""+str(mismatch_extra_total)+"""

How many conll arcs in total.
Final Total:\t\t\t\t""" +str(final_total)+"""

------------------------------------------------------------
MATCHES
------------------------------------------------------------
Of the matches, which link labels are associated with conll labels?
Matches:
"""
matches = list(all_matches.keys())
matches.sort()
for match in matches:
    result += match+":\t"
    temp = list(all_matches[match])
    temp.sort()
    result += str(temp)+"\n"

result += """
From the matches of the previous list. What are the counts?
Match Counts:
"""
pairs = list(all_match_counts.keys())
pairs.sort()

for pair in pairs:
    result += str(pair[0])+",\t"+str(pair[1])+"\t"+str(all_match_counts[pair])+"\n"
result += "\n"


result += """------------------------------------------------------------
EXTRA LINKS
------------------------------------------------------------
From the extra links. What are the counts?
Extra Counts:
"""
keys = list(all_extra_counts.keys())
keys.sort()
for key in keys:
    result += key+",\t"+str(all_extra_counts[key])+"\n"
result += "\n"



result += """------------------------------------------------------------
DIRECTIONALITY MISMATCHES
------------------------------------------------------------
Which links had different directionality to the conll?
"""
mismatches = list(mismatch_directionality.keys())
mismatches.sort()
for mismatch in mismatches:
    result += str(mismatch)+":\t"
    temp = list(mismatch_directionality[mismatch])
    temp.sort()
    result += str(temp)+"\n"
result += "\n"
#pprint(mismatch_directionality)


result += """From the directionality mismatches, what are the counts?
"""
#pprint(mismatch_directionality_counts)
pairs = list(mismatch_directionality_counts.keys())
pairs.sort()

for pair in pairs:
    result += str(pair[0])+",\t"+str(pair[1])+"\t"+str(mismatch_directionality_counts[pair])+"\n"
result += "\n"


result += """------------------------------------------------------------
THE EXTRA LINKS IN THE DIRECTIONAL MISMATCH CASES
------------------------------------------------------------
Of the cases where the links had different directionality, what are the "extra" links?
"""
mismatch_extras = list(mismatch_extra_counts.keys())
mismatch_extras.sort()

for mismatch_extra in mismatch_extras:
    result += str(mismatch_extra)+":\t"
    temp = str(mismatch_extra_counts[mismatch_extra])
    result += temp+"\n"
result += "\n"

#print mismatch_extra_total

f = open(ANALYSIS_FILE, "w+")
f.write(result)
f.close()




