#!/bin/sh


RUNTIMES="/tmp/LinksToDAG_times"
rm -f $RUNTIMES


typeset -i i END
END=100

for ((i=1;i<=$END;i++));
do
    bash src/tools/experiments/trial.sh data/english_bnews_train.sentences $i
done
python src/tools/plotter.py -x "Sentences" -y "Runtime (seconds)" -o "sol/runtimes.png" $RUNTIMES




python src/tools/experiments/analysis.py
python src/tools/plotter.py -x "Sentences" -y "Precision" -o "sol/precision_recall/precision.png" "sol/precision_recall/precision.txt"
python src/tools/plotter.py -x "Sentences" -y "Recall" -o "sol/precision_recall/recall.png" "sol/precision_recall/recall.txt"



#echo $RUNTIMES $END | mutt -s $END -a $RUNTIMES -- junekihong@gmail.com
