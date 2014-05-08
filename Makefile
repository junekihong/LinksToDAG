


# Paper
paper:
	cd doc; pdflatex LinksToDAG.tex -output-format pdf -halt-on-error -file-line-error

clean_paper:
	cd doc; ./clean.sh

# Graphs
graph_runtime:
	python src/tools/plotter.py -x "Sentences" -y "Runtime (seconds)" -o "sol/runtimes/runtimes.png" sol/runtimes/runtimes.txt
	cp sol/runtimes/runtimes.png doc

graph_precision:
	python src/tools/plotter.py -x "Sentences" -y "Precision" -o "sol/precision_recall/precision.png" sol/precision_recall/precision.txt
	cp sol/precision_recall/precision.png doc

graph_recall:
	python src/tools/plotter.py -x "Sentences" -y "Recall" -o "sol/precision_recall/recall.png" sol/precision_recall/recall.txt
	cp sol/precision_recall/recall.png doc

graph: graph_recall graph_precision graph_runtime
