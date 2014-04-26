#!/bin/sh

#./LinksToDAG data/mini.sentences 100
#./LinksToDAG data/mini.sentences 200
#./LinksToDAG data/mini.sentences 300


DATA=$1
ITERATIONS=$2
/usr/bin/time -f "%e" timeout 1800 ./LinksToDAG $DATA $ITERATIONS 2> output_error

echo -n $ITERATIONS " " >> /tmp/LinksToDAG_times
tail --lines 1 output_error >> /tmp/LinksToDAG_times
