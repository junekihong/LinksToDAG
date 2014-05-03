#!/bin/sh

DATA=$1
ITERATIONS=$2

mkdir -p /tmp/LinksToDAG_trial_sol/

/usr/bin/time -f "%e" timeout 1800 ./LinksToDAG $DATA $ITERATIONS 2> output_error

echo -n $ITERATIONS " " >> /tmp/LinksToDAG_times
tail --lines 1 output_error >> /tmp/LinksToDAG_times


cp sol/allowedLinks.txt /tmp/LinksToDAG_trial_sol/allowedLinks_$ITERATIONS.txt
rm -f output_error