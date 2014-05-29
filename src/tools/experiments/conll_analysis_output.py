#!/usr/bin/python

import sys, os
from pprint import pprint
from tikz_dependency import *
from dependency_graph import *

def result_numbers(final_total, 
                   match_total, 
                   extra_total, 
                   mismatch_total, 
                   reverse_match_total,
                   multiheaded_word_count, 
                   word_count_total, 
                   dropped_sentence_count,
                   multiheaded_sentence_count, 
                   original_sentence_count,
                   link_sentence_total,
                   link_remaining_sentences):


    match_percent = str(0)
    mismatch_percent = str(0)
    if final_total != 0:
        match_percent = str(float(match_total)/final_total)
        mismatch_percent = str(float(mismatch_total)/final_total)

    directional_percent = str(0)
    if mismatch_total != 0:
        directional_percent = str(float(reverse_match_total)/mismatch_total)

    multiheaded_word_percent = str(0)
    if word_count_total != 0:
        multiheaded_word_percent = str(float(multiheaded_word_count)/word_count_total)


    return """------------------------------------------------------------
ARC-LINK TOTALS
------------------------------------------------------------

How many conll arcs match a link. In both attachment and directionality.
Match Total:\t\t\t\t"""+ str(match_total)+""" 
Percent of all arcs:\t\t\t"""+ match_percent +"""

How many conll arcs do not match a link in only directionality?
Directional Mismatch Total:\t\t"""+str(reverse_match_total)+"""
Percent of all arcs:\t\t\t"""+ str(float(reverse_match_total) / final_total)+"""
Percent of all mismatches:\t\t"""+ directional_percent +"""

How many conll arcs do not match a link. In either attachment or directionality.
Mismatch Total:\t\t\t\t"""+str(mismatch_total)+"""\t
Percent of all arcs:\t\t\t"""+ mismatch_percent +"""

How many conll arcs in total.
Final Total:\t\t\t\t""" +str(final_total)+"""


------------------------------------------------------------
MISMATCHES
------------------------------------------------------------

------------------------------------------------------------
EXTRA LINKS
------------------------------------------------------------

How many links attach to a word when there is already a matching link to the conll data. How many "extra" arcs.
Extra Total:\t\t\t\t"""+str(extra_total)+"""


------------------------------------------------------------
WORDS
------------------------------------------------------------

How many multiheaded words there are.
Multiheaded Words:\t\t\t"""+str(multiheaded_word_count)+"""
Percent of all words:\t\t\t"""+multiheaded_word_percent+"""

Total number of all words:\t\t"""+str(word_count_total)+"""


------------------------------------------------------------
SENTENCES
------------------------------------------------------------

Total number of sentences with dropped words:
Dropped Sentences:\t\t\t"""+str(dropped_sentence_count)+"""
Percent of link sentences that were dropped:\t"""+str(float(dropped_sentence_count) / link_sentence_total)+"""

Total number of sentences with multiheaded words:
Multiheaded Sentences:\t\t\t"""+str(multiheaded_sentence_count)+"""
Percent of Sentences analyzed:\t\t"""+str(float(multiheaded_sentence_count) / link_remaining_sentences)+"""

Original Sentence Count:
\t\t\t\t\t"""+str(original_sentence_count)+"""

Total Sentence Count given after skipping the disconnected sentences in the link parser:
\t\t\t\t\t"""+str(link_sentence_total)+"""
\t\t\t\t\t("""+str(float(link_sentence_total)/original_sentence_count)+""") of original sentences

Total Sentence Count used in this analysis:
\t\t\t\t\t"""+str(link_remaining_sentences)+"""
\t\t\t\t\t("""+str(float(link_remaining_sentences)/original_sentence_count)+""") of original sentences
"""




#How many other links attach to a word when there is a directional mis-matching link to the conll data ?
#Directional Mismatch Extra Total:\t"""+str(mismatch_extra_total)+"""





def result_matches(all_matches, all_match_counts, all_extra_counts, all_blank_counts, mismatch_directionality, mismatch_directionality_counts, mismatch_extra_counts):
    result = """
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

  





def result_latex_corpus(original_sentence_count,
                        link_sentence_total, 
                        conll_analysis_sentence_count):

    result = ""
    result += "\t\\begin{tabular}{|l|l|}\n"
    result += "\t\t\\hline\n"
    result += "\t\tOriginal number of sentences in conll corpus & "+str(original_sentence_count)+"\\\\ \n"
    result += "\t\t\\hline\n"
    result += "\t\tSentences after discarding disconnected parses & "+str(link_sentence_total)+"\\\\ \n"
    result += "\t\t\\hline\n"
    result += "\t\tSentences used for experiment and analysis & "+str(conll_analysis_sentence_count)+"\\\\ \n"
    result += "\t\t\\hline\n"
    result += "\t\\end{tabular}\n"

    return result



