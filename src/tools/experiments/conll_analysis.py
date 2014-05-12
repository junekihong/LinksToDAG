#!/usr/bin/python

import os
from pprint import pprint

CONLL_DIR = "data/"
SOL_DIR = "sol/"

CONLL_LOC = CONLL_DIR+"english_bnews_train.conll"
SOL_LOC = SOL_DIR+"links.conll"

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
        conll_results[" ".join(sentence)] = tuple(conll)
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
    if not line:
        link_results[" ".join(sentence)] = tuple(conll)
        sentence = []
        conll = []
    else:
        conll.append(line)
        word = line.split()[1]
        
        # Get rid of the [] brackets around words that the link-parser could not attach.
        word = word.strip("[]")
        sentence.append(word)



def analysis(conlls, links):
    # How many links match the conll corpus
    matches = 0
    mismatches = 0
    extras = 0
    total = 0

    label_match = {}
    label_match_count = {}

    label_extra_count = {}

    # Directionality mismatch
    dir_miss = 0
    dir_miss_labels = {}
    dir_miss_labels_count = {}

    for conll,link in zip(conlls, links):
        conll = conll.split()
        link = link.split()

        conll_head = conll[6]
        link_heads = link[6].split(",")
        conll_label = conll[7]
        link_labels = link[7].split(",")

        if conll_head not in link_heads:
            head = int(conll[6])-1

            candidate = links[head]
            candidate = candidate.split()
            candidate_heads = candidate[6].split(",")
            candidate_labels = candidate[7].split(",")

            index = conll[0]
            
            for head,label in zip(candidate_heads,candidate_labels):
                if head == index:
                    dir_miss += 1
                    dir_miss_labels[conll_label] = dir_miss_labels.get(conll_label,set([])).union(set([label]))
                    dir_miss_labels_count[(conll_label,label)] = dir_miss_labels_count.get((conll_label,label),0)+1

            mismatches += 1
        else:
            for head,label in zip(link_heads, link_labels):
                if head == conll_head:
                    #print conll[0], conll[1], head
                    matches += 1 
                    label_match[conll_label] = label_match.get(conll_label, set([])).union(set([label]))
                    label_match_count[(conll_label,label)] = label_match_count.get((conll_label,label), 0) + 1
                else:
                    extras += 1
                    #label_extra = label_extra.union(set([label]))
                    label_extra_count[label] = label_extra_count.get(label, 0) + 1

        total += 1

    match_data = (matches, label_match, label_match_count)

    dir_miss_data = (dir_miss, dir_miss_labels, dir_miss_labels_count)
    mismatch_data = (mismatches, dir_miss_data)

    extra_data = (extras, label_extra_count)
    return (match_data, mismatch_data, extra_data, total)





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

for linkSentence in link_results:
    #print link_results[linkSentence]

    if linkSentence in conll_results:
        
        (match_data, mismatch_data, extra_data, total) = analysis(conll_results[linkSentence], link_results[linkSentence])
        (matches, label_match, label_match_count) = match_data
        (mismatches, dir_miss_data) = mismatch_data
        (dir_miss, dir_miss_labels, dir_miss_labels_count) = dir_miss_data

        (extras, label_extra_count) = extra_data

        match_total += matches
        mismatch_total += mismatches
        dir_mismatch_total += dir_miss

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
Match Total:\t\t\t"""+ str(match_total)+""" 
Percent of all arcs:\t\t"""+ match_percent +"""

How many conll arcs do not match a link. In either attachment or directionality.
Mismatch Total:\t\t\t"""+str(mismatch_total)+"""\t
Percent of all arcs:\t\t"""+ mismatch_percent +"""

How many conll arcs do not match a link in only directionality?
Directional Mismatch Total:\t"""+str(dir_mismatch_total)+"""
Percent of all mismatches:\t"""+ directional_percent +"""


How many links attach to a word when there is already a matching link to the conll data. How many "extra" arcs.
Extra Total:\t\t\t"""+str(extra_total)+"""

How many conll arcs in total.
Final Total:\t\t\t""" +str(final_total)+"""

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



f = open(ANALYSIS_FILE, "w+")
f.write(result)
f.close()




