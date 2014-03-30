#!/bin/sh

#./LinksToDAG data/mini.sentences 100
#./LinksToDAG data/mini.sentences 200
#./LinksToDAG data/mini.sentences 300


DATA=$1
ITERATIONS=$2
/usr/bin/time -f "%e" ./LinksToDAG $DATA $ITERATIONS >> output 2>> output_errors

echo $ITERATIONS >> times
tail --lines 1 output >> times
