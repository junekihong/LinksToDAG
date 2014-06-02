#!/usr/bin/python

import sys, os, operator 
from pprint import pprint
from tikz_dependency import *
from dependency_graph import *
from conll_analysis_output import *

DEBUG = False

# The directory containing the original conll data file
CONLL_DIR = "data/"
CONLL_LOC = CONLL_DIR+"english_bnews_train.conll"
if len(sys.argv) > 2:
    CONLL_LOC = sys.argv[2]
if not os.path.exists(CONLL_DIR):
    os.makedirs(CONLL_DIR)

# The directory containing our link-conll result data file
SOL_DIR = "sol/"
SOL_LOC = SOL_DIR+"links.conll"
if not os.path.exists(SOL_DIR):
    os.makedirs(SOL_DIR)

# Analysis directory and files. Where we will store these results.
ANALYSIS_DIR = "sol/conll_analysis/"
ANALYSIS_FILE = ANALYSIS_DIR+"conll_analysis.txt"
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)

# The trial number. How many sentences we take in originally.
TRIAL_NUM = 0
if len(sys.argv) > 3:
    TRIAL_NUM = int(sys.argv[3])

# Latex directory and files. Where we will store these results in latex form.
LATEX_DIR = "doc/figure/"
LATEX_FILE_SENTENCE = LATEX_DIR+"conll_analysis_sentences.tex"
LATEX_FILE_SENTENCE_DISCONNECTED = LATEX_DIR+"conll_analysis_sentences_disconnected.tex"
LATEX_FILE_SENTENCE_DROPPED = LATEX_DIR+"conll_analysis_sentences_dropped.tex"
LATEX_FILE_SENTENCE_MULTIHEADED = LATEX_DIR+"conll_analysis_sentences_multiheaded.tex"
LATEX_FILE_SENTENCE_TOTAL = LATEX_DIR+"conll_analysis_sentences_total.tex"
LATEX_FILE_ARCS = LATEX_DIR+"conll_analysis_arcs.tex"
if not os.path.exists(LATEX_DIR):
    os.makedirs(LATEX_DIR)

# Tikz directory and files
TIKZ_DIR = "doc/figure/"
EXAMPLE_SENTENCES_LOC = TIKZ_DIR+"sentences.tikz"
if not os.path.exists(TIKZ_DIR):
    os.makedirs(TIKZ_DIR)
PAPER_TIKZ = open(EXAMPLE_SENTENCES_LOC, 'w+')

EXAMPLE_PARSES_LOC = TIKZ_DIR+"parses.tikz"
EXAMPLE_PARSES = open(EXAMPLE_PARSES_LOC, 'w+')



# --------------------------------------------------------------------
# Analysis while reading in data. Pertains mostly to sentence counts
# --------------------------------------------------------------------
# Number of sentences from the link data
link_sentence_total = 0
link_dropped_sentences = 0
link_remaining_sentences = 0

# These maps will map a sentence to its conll representation.
# We will use this to query conll results from both our conll and link-conll files
conll_results = {}
link_results = {}



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
    #blanks = 0
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
    mismatch_data = (mismatches)

    return (match_data, reverse_data, extra_data, word_data, mismatch_data, total)


# Counts the word tokens that are multiheaded or dropped. Compared with the total number of word tokens
def analysis_words(conlls,links):
    word_count = 0
    
    multiheaded_count = 0
    isMultiheaded = False
    #dropped_word_count = 0        
    #hasDropped = False
    
    word_count += len(links)
    for conll,link in zip(conlls,links):
        link = link.split()
        """
        if link[6] == "-":
            dropped_word_count += 1
            hasDropped = True
        """

        link_heads = link[6].split(",")

        if len(link_heads) > 1:
            multiheaded_count += 1
            isMultiheaded = True

    multiheaded_data = (multiheaded_count, isMultiheaded)
    #dropped_data = (dropped_word_count, hasDropped)
    #return (dropped_data, multiheaded_data, word_count)
    return (multiheaded_data, word_count)




# Analysis on the links. For the appendix of the paper
def analysis_links(links):
    link_direction_counts = {}
    
    for link in links:
        link = link.split()
        index = int(link[0])
        heads = link[6].split(",")
        labels = link[7].split(",")

        for (head,label) in zip(heads,labels):
            head = int(head)

            link_direction_counts[label] = link_direction_counts.get(label,{})
            if head < index:
                link_direction_counts[label]["left"] = link_direction_counts[label].get("left",0) + 1
            elif head > index:
                link_direction_counts[label]["right"] = link_direction_counts[label].get("right",0) + 1

    return link_direction_counts




# Populating the link_results
f = open(SOL_LOC)
f = f.readlines()
sentence = []
conll = []

skipSentence = False
for line in f:
    line = line.strip()

    if not line:
        if skipSentence:
            link_dropped_sentences += 1
            skipSentence = False
        else:
            if "RIGHT-WALL" in sentence:
                sentence = sentence[:-1]

            # The sentence is stored as lower case.
            ID = " ".join(sentence)
            ID = ID.lower()
            link_results[ID] = tuple(conll)


        
        sentence = []
        conll = []
        link_sentence_total += 1
    else:
        conll.append(line)
        word = line.split()[1]

        if word.rfind("[") != -1 and word.rfind("]") != -1 and word.rfind("[!]") == -1:
            skipSentence = True


        # Remove the [!] at the end of words that link parser could not recognize
        index = -1
        index = word.rfind("[!]")
        if index != -1:
            word = word[:(index)]

        """index = -1
        index = word.rfind("[?]")
        if index != -1:
            word = word[:index]+word[index+len("[?]"):]
        print word"""



        # Get rid of the [] brackets around words that the link-parser could not attach.        
        #word = word.strip("[]")
        sentence.append(word)


link_remaining_sentences = link_sentence_total - link_dropped_sentences
if DEBUG:
    print "link_sentence_total", link_sentence_total
    print "link_dropped_sentences", link_dropped_sentences
    print "link_remaining_sentences", link_remaining_sentences
    print "percent dropped sentences", float(link_dropped_sentences) / link_sentence_total
    print "percent remaining sentences", float(link_remaining_sentences) / link_sentence_total
    print


# Populating the conll_results
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
        


        # Check to see if the sentence is in the link data. 
        # This is a small optimization. We don't need to store all of the conll data. 
        if ID in link_results:
            conll_results[ID] = tuple(conll)

        sentence = []
        conll = []
    else:
        conll.append(line)
        word = line.split()[1]
        sentence.append(word)

        

# --------------------------------------------------------------------
# Variables for the link analysis
# --------------------------------------------------------------------
arc_total = 0

match_total = 0
all_matches = {}
all_match_counts = {}

extra_total = 0
all_extra_counts = {}

#blank_total = 0
#all_blank_counts = {}

mismatch_total = 0
reverse_match_total = 0
mismatch_directionality = {}
mismatch_directionality_counts = {}

#mismatch_extra_total = 0
#mismatch_extra_counts = {}

link_direction_totals = {}

# --------------------------------------------------------------------
# Variables for word analysis
# --------------------------------------------------------------------
multiheaded_word_count = 0
dropped_word_total = 0
word_count_total = 0

multiheaded_sentence_count = 0


# --------------------------------------------------------------------
# Variables for the sentences used in the tikz output
# --------------------------------------------------------------------
paper_sentence_count = 0
paper_sentence_skip = 0
paper_sentence_limit = 3

example_parses_count = 0
example_parses_limit = 100


for linkSentence in link_results:
    if linkSentence not in conll_results:
        continue


    sentenceCheck = True
    linkSentenceCheck = linkSentence.split()
    # I am preventing certain sentences from appearing in the paper.
    # I just wanted to skip over some sentences because they didn't look cool enough
    #bannedWords = ["salees", "soldiers", "word", "serwer", "reason"]
    bannedWords = []
    for word in bannedWords:
        if word in linkSentenceCheck:
            sentenceCheck = False
            break

    # Link parses to put in the paper. Takes sentences of only length 5.
    if (paper_sentence_count < paper_sentence_limit) and len(linkSentence.split()) == 5 and sentenceCheck:
        if paper_sentence_skip > 0:
            paper_sentence_skip -= 1
        else:
            tikz = tikz_dependency(conll_results[linkSentence], link_results[linkSentence], linkSentence, .97 / 3)            
            PAPER_TIKZ.write(tikz)
            paper_sentence_count += 1
            if paper_sentence_count % 3 == 0:
                PAPER_TIKZ.write("\n")
    # Filter out sentences to only up to length 16
    elif example_parses_count < example_parses_limit and len(linkSentence) <= 85:
        tikz = tikz_dependency(conll_results[linkSentence], link_results[linkSentence], linkSentence, 1.0, False)
        EXAMPLE_PARSES.write("\\begin{figure*}[ht!]\n")
        EXAMPLE_PARSES.write(tikz)
        EXAMPLE_PARSES.write("\\end{figure*}\n\n")
        example_parses_count += 1
        if example_parses_count % 3 == 0:
            EXAMPLE_PARSES.write("\clearpage")


    # analysis_links
    link_direction_counts = analysis_links(link_results[linkSentence])
    for label in link_direction_counts:
        link_direction_totals[label] = link_direction_totals.get(label,{})
        for direction in link_direction_counts[label]:
            link_direction_totals[label][direction] = link_direction_totals[label].get(direction, 0) + link_direction_counts[label][direction]



    (match_data, reverse_data, extra_data, word_data, mismatch_data, total) = analysis(conll_results[linkSentence], link_results[linkSentence])

    (matches, label_match, label_match_count)                           = match_data
    (reverse_matches, label_reverse, label_reverse_count)               = reverse_data
    (extras, label_extra, label_extra_count)                            = extra_data

    (mismatches)                                                = mismatch_data 
    (multiheaded_data, word_count)                        = word_data

    #(dropped_word_count, hasDropped)                                    = dropped_data
    (multiheaded_count, isMultiheaded)                                  = multiheaded_data

    match_total += matches
    #blank_total += blanks
    reverse_match_total += reverse_matches
    mismatch_total += mismatches

    extra_total += extras
    arc_total += total

    multiheaded_word_count += multiheaded_count
    #dropped_word_total += dropped_word_count
    word_count_total += word_count

    if isMultiheaded:
        multiheaded_sentence_count += 1 

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



f = open(ANALYSIS_FILE, "w+")
result = result_numbers(arc_total, 
                        match_total, 
                        extra_total, 
                        #blank_total, 
                        mismatch_total, 
                        reverse_match_total, 
                        #mismatch_extra_total, 
                        #dropped_word_total,
                        multiheaded_word_count, 
                        word_count_total, 
                        link_dropped_sentences,
                        multiheaded_sentence_count, 
                        TRIAL_NUM,
                        link_sentence_total,
                        link_remaining_sentences)
                        

f.write(result)
f.close()



result = result_latex_corpus(TRIAL_NUM, 
                             link_sentence_total, 
                             link_remaining_sentences)
f = open(LATEX_FILE_SENTENCE, "w+")
f.write(result)
f.close()

result = result_latex_arcs(match_total, reverse_match_total, mismatch_total, arc_total)
f = open(LATEX_FILE_ARCS, "w+")
f.write(result)
f.close()


#---------------------------------------------------------------------
# Take our generated numbers and put them in latex files 
# to be called by the paper
#---------------------------------------------------------------------
disconnected_sentence_percentage = "{:.2f}".format(float(TRIAL_NUM - link_sentence_total) / TRIAL_NUM * 100)+"\\%"
dropped_sentence_percentage = "{:.2f}".format(float(link_dropped_sentences) / link_sentence_total * 100)+"\\%"
multiheaded_sentence_percentage = float(multiheaded_sentence_count) / link_remaining_sentences * 100
multiheaded_sentence_percentage = "{:.2f}".format(multiheaded_sentence_percentage)+"\\%"
f = open(LATEX_FILE_SENTENCE_DISCONNECTED, "w+")
f.write(disconnected_sentence_percentage)
f.close()

f = open(LATEX_FILE_SENTENCE_DROPPED, "w+")
f.write(dropped_sentence_percentage)
f.close()

f = open(LATEX_FILE_SENTENCE_MULTIHEADED, "w+")
f.write(multiheaded_sentence_percentage)
f.close()

f = open(LATEX_FILE_SENTENCE_TOTAL, "w+")
f.write("{:,d}".format(link_sentence_total))
f.close()



#print result


#print "ALL MATCH COUNTS"
#pprint(all_match_counts)
#print

#print "MISMATCH DIRECTIONALITY COUNTS"
#pprint(mismatch_directionality_counts)
#print






#---------------------------------------------------------------------
# Setting up the matching link label counts and majority predictions
# This will be used in a table of the appendix of the paper
#---------------------------------------------------------------------
link_label_prediction = {}
for (label_conll, label_link) in all_match_counts:
    link_label_prediction[label_link] = link_label_prediction.get(label_link, {})
    link_label_prediction[label_link][label_conll] = link_label_prediction[label_link].get(label_conll, 0)
    link_label_prediction[label_link][label_conll] += all_match_counts[(label_conll, label_link)]

for (label_conll, label_link) in mismatch_directionality_counts:
    link_label_prediction[label_link] = link_label_prediction.get(label_link, {})
    link_label_prediction[label_link][label_conll] = link_label_prediction[label_link].get(label_conll, 0)
    link_label_prediction[label_link][label_conll] += mismatch_directionality_counts[(label_conll, label_link)]

# Gives us total counts. The normalizing constants to use later.
link_label_prediction_totals = {}
for label in link_label_prediction:
    conlls = link_label_prediction[label]
    count = 0
    for conll in conlls:
        count += conlls[conll]
    link_label_prediction_totals[label] = count

predictions = {}
for label_link in link_label_prediction:
    conll_map = link_label_prediction[label_link]
    predictions[label_link] = max(conll_map.iteritems(), key=operator.itemgetter(1))[0]

#pprint(predictions)
#pprint(link_label_prediction)


#---------------------------------------------------------------------
# Setting up Link label counts 
# which is used for a table in the appendix of the paper
#---------------------------------------------------------------------
#pprint(link_direction_totals)
link_label_counts = {}
for label in link_direction_totals:
    count = 0
    for direction in link_direction_totals[label]:
        count += link_direction_totals[label][direction]
    link_label_counts[label] = count
labels = link_label_counts.keys()
labels.sort()

#---------------------------------------------------------------------
# Analysis/counts of the links, their labels, and their directions
# For the appendix section of the paper
#---------------------------------------------------------------------
LATEX_FILE_LINKS = LATEX_DIR+"link_analysis_table.tex"
f = open(LATEX_FILE_LINKS, "w+")
latex_table = "\\begin{tabular}{|l|l|l|l||l|l|}\n"
header = "Label & Count & Left & Right & CoNLL & CoNLL Percentage\\\\ \n"

begin_figure = "\\begin{figure*}\n"
end_figure = "\\end{figure*}\n"

table = begin_figure
table += latex_table
table += "\\hline\n"
table += header
line = 0
for label in labels:
    count = link_label_counts[label]
    
    left = link_direction_totals[label].get("left",0)
    left = str(int(float(left) / count * 100))+"\\%" + " ("+str(left)+")"
    right = link_direction_totals[label].get("right",0)
    right = str(int(float(right) / count * 100))+"\\%" + " ("+str(right)+")"

    prediction = predictions.get(label, "-")
    prediction_num = ""
    prediction_total = ""
    prediction_percent = ""
    if prediction != "-":
        prediction_num = link_label_prediction[label][prediction]
        prediction_total = link_label_prediction_totals[label]
    if prediction_num and prediction_total:
        prediction_percent = str(int(float(prediction_num) / prediction_total * 100)) + "\\%" + " (" + str(prediction_num) + "/" + str(prediction_total) + ")"


    table += "\\hline\n"
    table += " "+label+" & "+str(count)+" & "+left+" & "+right+" & "+prediction+" & "+prediction_percent+" \\\\ \n"
    line += 1
    
    # Break up the table into smaller tables
    if line % 50 == 0:
        table += "\\hline\n"
        table += "\\end{tabular}\n"
        table += end_figure
        table += begin_figure
        table += latex_table
        table += "\\hline\n"
        table += header
    
table += "\\hline\n"
table += "\\end{tabular}\n"
table += end_figure

f.write(table)
f.close()













