#!/bin/sh


RUNTIMES="/tmp/LinksToDAG_times"
rm -f $RUNTIMES


typeset -i i END
END=100

for ((i=1;i<=$END;i++));
do
    bash src/tools/trial.sh data/english_bnews_train.sentences $i
done






#cat /tmp/LinksToDAG_times
python src/tools/plotter.py $RUNTIMES



echo $RUNTIMES $END | mutt -s $END -a $RUNTIMES -- junekihong@gmail.com
