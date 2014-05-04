#!/bin/sh


RUNTIMES="/tmp/LinksToDAG_times"
SOL_RUNTIME="sol/runtimes.png"

PRECISION_RECALL="sol/precision_recall/"
TXT_PRECISION=$PRECISION_RECALL"precision.txt"
TXT_RECALL=$PRECISION_RECALL"recall.txt"
SOL_PRECISION=$PRECISION_RECALL"precision.png"
SOL_RECALL=$PRECISION_RECALL"recall.png"

TYPE_AGREEMENT="sol/type_agreement/"
TYPE_ANALYSIS=$TYPE_AGREEMENT"type_analysis.txt"



rm -f $RUNTIMES $TXT_RUNTIME $SOL_RUNTIME $TXT_PRECISION $SOL_PRECISION $SOL_RECALL
rm -rf /tmp/LinksToDAG_trial_sol/

typeset -i i END
END=10

for ((i=1;i<=$END;i++));
do
    bash src/tools/experiments/trial.sh data/english_bnews_train.sentences $i
done


python src/tools/plotter.py -x "Sentences" -y "Runtime (seconds)" -o $SOL_RUNTIME $RUNTIMES




python src/tools/experiments/analysis.py
python src/tools/plotter.py -x "Sentences" -y "Precision" -o $SOL_PRECISION $TXT_PRECISION
python src/tools/plotter.py -x "Sentences" -y "Recall" -o $SOL_RECALL $TXT_RECALL



echo $RUNTIMES $END | mutt -s $END -a $RUNTIMES -a $TXT_PRECISION -a $TXT_RECALL -a $TYPE_ANALYSIS -- junekihong@gmail.com
