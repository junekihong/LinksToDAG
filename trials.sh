#!/bin/sh


RUNTIMES="/tmp/LinksToDAG_times"
rm -f $RUNTIMES

#trials=( 1 10 25 50 75 100 125 150 175 200 )



#trials=( 1 10 25 50 75 100 110 120 )
#125 150 175 200 )

#if [ $1 ]; 
#then 
#    trials=( $1 $1 $1 $1 $1 $1 $1 $1 $1 $1 )
#else
#    trials=( 100 100 100 100 100 100 100 100 100 100 )
#fi

#trials=( 1 2 )


typeset -i i END
END=130

#for i in "${trials[@]}"
for ((i=1;i<=$END;i++));
do
    bash tools/trial.sh data/mini.sentences $i
done






#cat /tmp/LinksToDAG_times
python src/plotter.py $RUNTIMES



echo $RUNTIMES | mutt -s $END -a $RUNTIMES -- junekihong@gmail.com
