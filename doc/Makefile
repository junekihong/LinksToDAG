
all:
	pdflatex LinksToDAG.tex -output-format pdf -halt-on-error -file-line-error && bibtex LinksToDAG.aux && pdflatex LinksToDAG.tex && pdflatex LinksToDAG.tex && (pdftk LinksToDAG.pdf cat 1-5 output body.pdf; pdftk LinksToDAG.pdf cat 6-end output supplement.pdf; zip supplement.zip supplement.pdf)

parses.pdf: figure/parses.tikz
	pdflatex parses.tex


clean:
	rm *.aux *.log
	rm *.blg 
	rm *.bbl


# Graphs
graph_runtime:
	python ../src/tools/plotter.py -x "Sentences" -y "Runtime (seconds)" -o "sol/runtimes/runtimes.png" ../sol/runtimes/runtimes.txt
	cp ../sol/runtimes/runtimes.png figure

graph_precision_recall:
	python ../src/tools/plotter.py -x Sentences -y Percent -o ../sol/precision_recall/precision_recall.png ../sol/precision_recall/precision.txt ../sol/precision_recall/recall.txt
	cp ../sol/precision_recall/precision_recall.png figure/

graphs: graph_precision_recall


