#!/bin/sh

typeset -i i END


#END=10000
END=60030
#END=10
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
SOL_PRECISION_RECALL=$PRECISION_RECALL"precision_recall.png"

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
cat $TXT_PRECISION | sort -V > temp; mv temp $TXT_PRECISION
cat $TXT_RECALL | sort -V > temp; mv temp $TXT_RECALL

python src/tools/plotter.py -x "Sentences" -y "Percent" -o $SOL_PRECISION_RECALL $TXT_PRECISION $TXT_RECALL



echo $RUNTIMES $END $'\n'The CLSP machines cant run plotter. Please download files and run: $'\n'python src/tools/plotter.py -x "Sentences" -y "Percent" -o $SOL_PRECISION_RECALL $TXT_PRECISION $TXT_RECALL | mutt -s $END -a $RUNTIMES -a $TXT_PRECISION -a $TXT_RECALL -a $TYPE_ANALYSIS -a $CONLL_ANALYSIS -- junekihong@gmail.com

