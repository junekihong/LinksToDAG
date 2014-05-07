

graph_runtime:
	python src/tools/plotter.py -x "Sentences" -y "Runtime (seconds)" -o "sol/runtimes/runtimes.png" sol/runtimes/runtimes.txt

graph_precision:
	python src/tools/plotter.py -x "Sentences" -y "Precision" -o "sol/precision_recall/precision.png" sol/precision_recall/precision.txt

graph_recall:
	python src/tools/plotter.py -x "Sentences" -y "Recall" -o "sol/precision_recall/recall.png" sol/precision_recall/recall.txt


graph: graph_recall graph_precision graph_runtime