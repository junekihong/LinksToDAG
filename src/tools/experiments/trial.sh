#!/bin/sh
mkdir -p /tmp/LinksToDAG_trial_sol/

DATA=$1
ITERATIONS=$2
LANGUAGE=$3


/usr/bin/time -f "%e" -o runtime ./LinksToDAG $DATA $ITERATIONS $LANGUAGE




<<BLOCK_COMMENT
BLOCK_COMMENT




echo -n $ITERATIONS " " >> /tmp/LinksToDAG_times
tail --lines 1 runtime >> /tmp/LinksToDAG_times




if [ $3 ]; then
    cp sol/allowedLinks.txt /tmp/LinksToDAG_trial_sol/allowedLinks_$ITERATIONS\_$LANGUAGE.txt
    
    python src/tools/experiments/conll_analysis.py
    mv sol/conll_analysis/conll_analysis.txt sol/conll_analysis/conll_analysis_$ITERATIONS\_$LANGUAGE.txt
else
    cp sol/allowedLinks.txt /tmp/LinksToDAG_trial_sol/allowedLinks_$ITERATIONS.txt
    
    python src/tools/experiments/conll_analysis.py
    mv sol/conll_analysis/conll_analysis.txt sol/conll_analysis/conll_analysis_$ITERATIONS.txt
fi

rm -f runtime


