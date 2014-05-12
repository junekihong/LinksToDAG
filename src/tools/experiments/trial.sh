#!/bin/sh

DATA=$1
ITERATIONS=$2

mkdir -p /tmp/LinksToDAG_trial_sol/

/usr/bin/time -f "%e" -o runtime ./LinksToDAG $DATA $ITERATIONS #2> output_error

echo -n $ITERATIONS " " >> /tmp/LinksToDAG_times
tail --lines 1 runtime >> /tmp/LinksToDAG_times


cp sol/allowedLinks.txt /tmp/LinksToDAG_trial_sol/allowedLinks_$ITERATIONS.txt
rm -f runtime


python src/tools/experiments/conll_analysis.py
mv sol/conll_analysis/conll_analysis.txt sol/conll_analysis/conll_analysis_$ITERATIONS.txt

