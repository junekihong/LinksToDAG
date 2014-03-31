#!/bin/sh

rm -f /tmp/LinksToDAG_times


#trials=( 1 10 25 50 75 100 125 150 175 200 )
trials=( 1 2 3 )

for i in "${trials[@]}"
do
    bash tools/trial.sh data/mini.sentences $i
done






#cat /tmp/LinksToDAG_times
python src/plotter.py /tmp/LinksToDAG_times