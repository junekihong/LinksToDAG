
clean_cache_SCIP:
	rm -f /tmp/LinksToDAG_SCIP_cache.p

clean_cache_linkparses:
	rm -f /tmp/LinksToDAG_linkparses_cache.p

clean: clean_cache_SCIP clean_cache_linkparses



# Paper
paper:
	cd doc; pdflatex LinksToDAG.tex -output-format pdf -halt-on-error -file-line-error

clean_paper:
	cd doc; ./clean.sh

# Graphs
graph_runtime:
	python src/tools/plotter.py -x "Sentences" -y "Runtime (seconds)" -o "sol/runtimes/runtimes.png" sol/runtimes/runtimes.txt
	cp sol/runtimes/runtimes.png doc

graph_precision_recall:
	python src/tools/plotter.py -x Sentences -y Percent -o sol/precision_recall/precision_recall.png sol/precision_recall/precision.txt sol/precision_recall/recall.txt
	cp sol/precision_recall/precision_recall.png doc/figure/

graph: graph_precision_recall
