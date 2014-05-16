#!/bin/sh

typeset -i i END


#END=10000
END=60030
#END=100
#INCREMENT=1

SENTENCES="data/english_bnews_train.sentences"
CONLL="data/english_bnews_train.conll"
LANGUAGE=""

if [ $1 ]; then
    SENTENCES=$1
fi
if [ $2 ]; then
    CONLL=$2
fi
if [ $3 ]; then
    LANGUAGE=$3
fi


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

CONLL_ANALYSIS="sol/conll_analysis/conll_analysis_"$END".txt"

for ((i=1;i<=$END;i=$((i*2))));
do
    bash src/tools/experiments/trial.sh $SENTENCES $CONLL $i $LANGUAGE
done

if [ $i -ne $END -a $((i/2)) -ne $END ]; then
    bash src/tools/experiments/trial.sh $SENTENCES $CONLL $END $LANGUAGE
fi

python src/tools/plotter.py -x "Sentences" -y "Runtime (seconds)" -o $SOL_RUNTIME $RUNTIMES




python src/tools/experiments/type_analysis.py 
python src/tools/plotter.py -x "Sentences" -y "Precision" -o $SOL_PRECISION $TXT_PRECISION
python src/tools/plotter.py -x "Sentences" -y "Recall" -o $SOL_RECALL $TXT_RECALL



#echo $RUNTIMES $END | mutt -s $END -a $RUNTIMES -a $TXT_PRECISION -a $TXT_RECALL -a $TYPE_ANALYSIS -a $CONLL_ANALYSIS -- junekihong@gmail.com
