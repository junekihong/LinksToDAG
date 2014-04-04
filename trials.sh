#!/bin/sh

rm -f /tmp/LinksToDAG_times


#trials=( 1 10 25 50 75 100 125 150 175 200 )
#trials=( )
typeset -i i END


END=50

#for i in "${trials[@]}"
for ((i=1;i<=$END;i++));
do
    bash tools/trial.sh data/mini.sentences $i
done






#cat /tmp/LinksToDAG_times
python src/plotter.py /tmp/LinksToDAG_times