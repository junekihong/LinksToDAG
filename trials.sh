#!/bin/sh

typeset -i i END


END=4096
#END=60030
#END=16384
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
    

# Run the trial_ru.sh script if we are doing russian trials
if [ $LANGUAGE -a $LANGUAGE = "ru" ]; then
    for ((i=1;i<=$END;i=$((i*2))));
    do
        bash src/tools/experiments/trial_ru.sh $SENTENCES $i
    done
    
    if [ $i -ne $END -a $((i/2)) -ne $END ]; then
        bash src/tools/experiments/trial_ru.sh $SENTENCES $END
    fi
else     
    for ((i=1;i<=$END;i=$((i*2))));
    do
        bash src/tools/experiments/trial.sh $SENTENCES $CONLL $i $LANGUAGE
    done

    if [ $i -ne $END -a $((i/2)) -ne $END ]; then
        bash src/tools/experiments/trial.sh $SENTENCES $CONLL $END $LANGUAGE
    fi
fi




python src/tools/plotter.py -x "Sentences" -y "Runtime (seconds)" -o $SOL_RUNTIME $RUNTIMES




python src/tools/experiments/type_analysis.py 
cat $TXT_PRECISION | sort -V > temp_precision; rm -f $TXT_PRECISION 
cat $TXT_RECALL | sort -V > temp_recall; rm -f $TXT_RECALL

if [ $LANGUAGE ]; then
    TXT_PRECISION=$PRECISION_RECALL"precision#"$LANGUAGE".txt"
    TXT_RECALL=$PRECISION_RECALL"recall#"$LANGUAGE".txt"

    mv temp_precision $TXT_PRECISION
    mv temp_recall $TXT_RECALL
    python src/tools/plotter.py -x "Sentences" -y "Percent" -o $PRECISION_RECALL"precision_recall#"$LANGUAGE".png" $TXT_PRECISION $TXT_RECALL
else
    TXT_PRECISION=$PRECISION_RECALL"precision#en.txt"
    TXT_RECALL=$PRECISION_RECALL"recall#en.txt"
    mv temp_precision $TXT_PRECISION
    mv temp_recall $TXT_RECALL
    python src/tools/plotter.py -x "Sentences" -y "Percent" -o $SOL_PRECISION_RECALL $TXT_PRECISION $TXT_RECALL
fi






#echo $RUNTIMES $END $'\n'The CLSP machines cant run plotter. Please download files and run: $'\n'python src/tools/plotter.py -x "Sentences" -y "Percent" -o $SOL_PRECISION_RECALL $TXT_PRECISION $TXT_RECALL | mutt -s $END -a $RUNTIMES -a $TXT_PRECISION -a $TXT_RECALL -- junekihong@gmail.com

#-a $TYPE_ANALYSIS -a $CONLL_ANALYSIS -- junekihong@gmail.com

