# Link Edge to DAG Zimpl file.
# Juneki Hong


# Data sets
# ----------

# Read in the data. (node1, node2, layer, label, sentence)
set LINK := { read "$LINKFILENAME$" as "<1n, 2n, 3n, 4s, 5n>" };

set LABELS := proj(LINK,<4>);
set DIRECTIONS := { 0, 1 };
set POSSIBLE_LABELS := LABELS * DIRECTIONS;

set NODE := proj(LINK,<1,5>) union proj(LINK,<2,5>);
set NODE_PAIR := { <i,sentence1,j,sentence2> in NODE * NODE with sentence1 == sentence2 and i < j };


# Variables.
# ----------


# Allowed Labels
var allowedLabel[POSSIBLE_LABELS];# binary;
# Direction
var direction[LINK] binary;

# Node has Parent
var hasParent[NODE];# binary;

# Node depth
var depth[NODE] >= 0;

# Slack
var slack[LABELS] >= 0;

# Left and Right links
var llink[NODE_PAIR];# binary;
var rlink[NODE_PAIR];# binary;



# Parameters.
# ----------

param corpusSize := $CORPUSSIZE$;
param size[<label> in LABELS] := sum <i,j,layer,label,sentence> in LINK: 1;
param cost[<label> in LABELS] := 100 / size[label];

# Objective and Constraints.
# ----------

# Minimize the number of allowed labels used.
#minimize labelsUsed : sum<label, dir> in POSSIBLE_LABELS : (allowedLabel[label,dir] + 100*slackLabel[label,dir]/size[label]);
minimize labelsUsed : sum<label> in LABELS : (allowedLabel[label,0] + allowedLabel[label,1] + cost[label]*slack[label]);


# Constraint: Every link gets an allowed label. The minimization objective should try to use the least amount of unique allowed labels.
#subto atLeastOneLabel : forall <i,j,layer,label,sentence> in LINK : allowedLabel[label,0] + allowedLabel[label, 1] + slackLabel[label,0] + slackLabel[label,1]>= 1;
#subto onlyOneAllowedLabel : forall <i,j,layer,label,sentence> in LINK : allowedLabel[label,0] == 1-allowedLabel[label,1];

subto atLeastOneLabel : forall <i,j,layer,label,sentence> in LINK : allowedLabel[label,0] + allowedLabel[label, 1] >= 1;



# Constraint: Set the direction variable to match the direction specified in allowedLabel
#subto assignLabel_L : forall <i,j,layer,label,sentence> in LINK : sum <label, 0> in POSSIBLE_LABELS : allowedLabel[label,0]+slackLabel[label,0] >= 1 - direction[i,j,layer,label,sentence];
#subto assignLabel_R : forall <i,j,layer,label,sentence> in LINK : sum <label, 1> in POSSIBLE_LABELS : allowedLabel[label,1]+slackLabel[label,1] >= direction[i,j,layer,label,sentence];

subto assignment : forall <label> in LABELS : size[label] == slack[label] + sum <i,j,layer,label,sentence> in LINK : (allowedLabel[label,0]*(1-direction[i,j,layer,label,sentence]) + allowedLabel[label,1]*direction[i,j,layer,label,sentence])
;
# If there are no links with the label that go in a direction, then we force allowedLabel in that direction to be 0.
# I think this isn't necessary for the program, but it may help the solver prune the search space a little better.
#subto assignment_L : forall <label> in LABELS : allowedLabel[label,0] <= sum<i,j,layer,label,sentence> in LINK : (1 - direction[i,j,layer,label,sentence]);
#subto assignment_R : forall <label> in LABELS : allowedLabel[label,1] <= sum<i,j,layer,label,sentence> in LINK : (direction[i,j,layer,label,sentence]);


# Constraints: left and right links in terms of the assigned direction
subto assign_llink : forall <i,j,layer,label,sentence> in LINK : llink[i,sentence, j, sentence] == 1 - direction[i,j,layer,label,sentence];
subto assign_rlink : forall <i,j,layer,label,sentence> in LINK : rlink[i,sentence, j, sentence] == direction[i,j,layer,label,sentence];

# Constraints: depth of the nodes. Used to handle acyclicity.
subto depth_zeroInitialization: forall <0,sentence> in NODE: depth[0,sentence] == 1;
subto depth_recursive_L: forall <i,sentence,j,sentence> in NODE_PAIR: depth[i,sentence] >= llink[i,sentence,j,sentence]*(depth[j,sentence] + 1);
subto depth_recursive_R: forall <i,sentence,j,sentence> in NODE_PAIR: depth[j,sentence] >= rlink[i,sentence,j,sentence]*(depth[i,sentence] + 1);

# Constraints: For every link one node is a parent of another.
subto everyLinkMakesAParent : forall<i,j,layer,label,sentence> in LINK : (hasParent[i,sentence]*llink[i,sentence,j,sentence] + hasParent[j,sentence]*rlink[i,sentence,j,sentence]) == 1;

# Constraints: If there are no links to a node, then that node cannot have a parent. 
subto noLinkThenNoParent : forall<j,sentence> in NODE : hasParent[j,sentence] <= sum<i,j,layer,label,sentence> in LINK : rlink[i,sentence,j,sentence] + sum<j,k,layer2,label2,sentence> in LINK : llink[j,sentence,k,sentence] ;

# Constraints: Everyone except the root has to have a parent. 
# TODO: If the parse is bad and the graph is disconnected, then we cannot handle it and the solver returns infeasable.
subto everyOneHasParent : forall<i,sentence> in NODE with i > 0 : hasParent[i,sentence] == 1;
subto rootHasNoParent : forall<0,sentence> in NODE : hasParent[0,sentence] == 0;

# ----------

