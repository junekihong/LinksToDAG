# Link Edge to DAG Zimpl file.
# Juneki Hong
# Jason Eisner

# TODO: If the parse is bad and the graph is disconnected, then we cannot handle it and the solver returns infeasable.


# ------------------------------------------------------------------------------
# Data sets
# ------------------------------------------------------------------------------

set LINK := { read "$LINKFILENAME$" as "<1n, 2n, 3n, 4s, 5n>" };    # An identification for each and every link across all parses.
                                                                    # (node1, node2, layer, label, sentence)
# TODO: Slack Hierarchy 
# Plan: (node1, node2, layer, coarseLabel, label, sentence)
# set LINK := { read "$LINKFILENAME$" as "<1n, 2n, 3n, 4s, 5s, 6n>" };

set LABELS := proj(LINK,<4>);                                                   # The labels of all the links.
set DIRECTIONS := { 0, 1 };                                                     # Possible directions for a link.
set POSSIBLE_LABELS := LABELS * DIRECTIONS;                                     # Possible (label,direction) pairs
set NODE := proj(LINK,<1,5>) union proj(LINK,<2,5>);                            # All possible tokens for each sentence.
set SENTENCES := proj(LINK,<5>);                                                # Sentence indices

# ------------------------------------------------------------------------------
# Parameters.
# ------------------------------------------------------------------------------

param corpusSize := sum <node,sentence> in NODE: 1;#$CORPUSSIZE$;                   # The number of tokens in the corpus.
param typeSize[<label> in LABELS] := sum <i,j,layer,label,sentence> in LINK: 1;     # The number of links that have a given label. For each label.
param tokenCost[<label> in LABELS] := 4 / typeSize[label];                        # The slack cost of a label given as a portion of typeSize[label]
# param maxSentenceLen := max <i,sentence> in NODE: i;                              # Maximum length of a sentence
# param sentenceLen[<sentence> in SENTENCES] := max <i,sentence> in NODE: i;        # Length of each sentence; presumably too slow in ZIMPL so we use a script to make an external file instead
param sentenceLen[SENTENCES] := read "$SENTLENFILENAME$" as "<1n> 2n";              # sentence numbers and lengths

#param coarseTypeSize[<coarse> in COARSE_LABELS] := sum <i,j,layer,label,coarse,sentence> in LINK: 1;
#param typeCost[<coarse> in COARSE_LABELS] := 1000 / coarseTypeSize[coarse]

# ------------------------------------------------------------------------------
# Variables.
# ------------------------------------------------------------------------------

var allowedLabel[POSSIBLE_LABELS];                                              # Allowed Labels
var rLink[LINK] binary;                                                         # Direction: 0 for left, 1 for right
var depth[NODE] >= 0;                                                           # Node depth
var tokenslack[LINK] >= 0;                                                      # Slack


# ------------------------------------------------------------------------------
# Objective and Constraints.
# ------------------------------------------------------------------------------

# Minimize the number of allowed labels used.
minimize stipulations: 
    (sum <label> in LABELS: 
        (allowedLabel[label,0] + allowedLabel[label,1])) +                       # number of directed types
    (sum <i,j,layer,label,sentence> in LINK: 
        tokenslack[i,j,layer,label,sentence] * tokenCost[label]) +               # number of directed tokens that aren't licensed by a directed type, times a token cost
    0.0001 * (sum <i,sentence> in NODE: 0.0001 * depth[i,sentence]);             # break ties by keeping depth small, other things equal -- might speed up LP simplex solver

# Jason thinks this is unnecessary. It seems to affect performance however. 
subto at_least_one_label: 
    forall <i,j,layer,label,sentence> in LINK: 
        allowedLabel[label,0] + allowedLabel[label, 1] >= 1;

# Check that links only go in allowed directions, except for slack.
subto left_token_ok:
    forall <i,j,layer,label,sentence> in LINK: 
        1-rLink[i,j,layer,label,sentence] <= allowedLabel[label,0] + tokenslack[i,j,layer,label,sentence];
subto right_token_ok:
    forall <i,j,layer,label,sentence> in LINK:
        rLink[i,j,layer,label,sentence] <= allowedLabel[label,1] + tokenslack[i,j,layer,label,sentence];

# # Assign a depth to each node, which must be greater than the depth of any parents it has. Used to enforce acyclicity.

subto depth_bound:
    forall <i,sentence> in NODE: depth[i,sentence] <= sentenceLen[sentence] + 1;

subto depth_recursive_L: 
    forall <i,j,layer,label,sentence> in LINK: 
        depth[i,sentence] + (1+sentenceLen[sentence])*rLink[i,j,layer,label,sentence] >= depth[j,sentence] + 1;  # skip constraint on i if right link i --> j
subto depth_recursive_R: 
    forall <i,j,layer,label,sentence> in LINK: 
        depth[j,sentence] + (1+sentenceLen[sentence])*(1-rLink[i,j,layer,label,sentence]) >= depth[i,sentence] + 1;  # skip constraint on j if left link i <-- j

# Jason thinks this is unnecessary, but it seems to affect performance.
subto depth_zero_initialization: 
    forall <0,sentence> in NODE: depth[0,sentence] == 1;   

# # The root has the smallest depth.
# subto root_depth:
#     forall <i,sentence> in NODE: depth[0,sentence] <= depth[i,sentence];

# Jason: may need to rewrite in terms of indexed sets if the pattern matching doesn't work
# Juneki: Constraint rewritten in terms of rLink.
subto every_token_has_parent: 
    forall <i,sentence> in NODE with i >= 1: 
        1 <= 
        (sum <i,j,layer,label,sentence> in LINK:
            (1-rLink[i,j,layer,label,sentence])) + 
        (sum <j,i,layer,label,sentence> in LINK:
            (rLink[j,i,layer,label,sentence]));




#subto s_right:
#      allowedLabel["S",0] == 0;
 

#subto s_left:
#      allowedLabel["S",1] == 0;
