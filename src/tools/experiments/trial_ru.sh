#!/bin/sh
mkdir -p /tmp/LinksToDAG_trial_sol/

SENTENCES=$1
ITERATIONS=$2
LANGUAGE="ru"



/usr/bin/time -f "%e" -o runtime ./LinksToDAG $SENTENCES $ITERATIONS $LANGUAGE




echo -n $ITERATIONS " " >> /tmp/LinksToDAG_times
tail --lines 1 runtime >> /tmp/LinksToDAG_times



if [ $LANGUAGE ]; then
    cp sol/allowedLinks.txt /tmp/LinksToDAG_trial_sol/allowedLinks_$ITERATIONS\_$LANGUAGE.txt
    #python src/tools/experiments/conll_analysis.py $SENTENCES $CONLL $ITERATIONS $LANGUAGE
    #mv sol/conll_analysis/conll_analysis.txt sol/conll_analysis/conll_analysis_$ITERATIONS\_$LANGUAGE.txt
else
    cp sol/allowedLinks.txt /tmp/LinksToDAG_trial_sol/allowedLinks_$ITERATIONS.txt
    #python src/tools/experiments/conll_analysis.py $SENTENCES $CONLL $ITERATIONS
    #mv sol/conll_analysis/conll_analysis.txt sol/conll_analysis/conll_analysis_$ITERATIONS.txt
fi

rm -f runtime


