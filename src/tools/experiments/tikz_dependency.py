#!/usr/bin/python
from dependency_graph import *


# Produces a tikz_dependency string that can be redirected to a latex file for display.
def tikz_dependency(conlls, links, sentence, ratio = 0.3, subfigure = True):

    result = ""
    if subfigure:
        ratio = "{0:.2f}".format(ratio)
        result += "\\begin{subfigure}[b]{"+ratio+"\\textwidth}\n"
    result += "\t\\begin{dependency}\n"
    result += "\t\t\\begin{deptext}\n"
        
    indices = []
    conll_heads = []
    conll_labels = []

    link_heads = []
    link_labels = []

    POS_conll = []
    POS_link = []

    graph_conll = getGraph(conlls)
    graph_link = getGraph(links)

    for POS in graph_conll.POS_sequence:
        POS_conll.append("{\\scriptsize "+POS+"}")

    link_sentence = " \& ".join(graph_link.sentence).replace("[", "\\lbrack ").replace("]", "\\rbrack")
    POS_sequence = " \& ".join(graph_link.POS_sequence).replace("$", "\\$")

    result += "\t\t\t" + " \& ".join(POS_conll) + " \\\\\n"
    result += "\t\t\t" + " \& ".join(graph_conll.sentence) + " \\\\\n"
    result += "\t\t\t" + " \\\\\n"
    result += "\t\t\t" + link_sentence + " \\\\\n"
    result += "\t\t\t" + POS_sequence + " \\\\\n"
    result += "\t\t\\end{deptext}\n"


    for head in graph_conll.table:
        children = graph_conll.table[head]
        for child in children:
            label = graph_conll.labels[(head,child)]
 
            if head in graph_link.table and child in graph_link.table[head]:
                result += tikz_draw_edge(head, child, graph_link.getEdge(head,child), "below", "thick")
                result += tikz_draw_edge(head, child, label, "above", "thick")
                graph_link.deleteEdge(head,child)

                #multiheads = graph_link.heads.get(child, [])
                #for multihead in multiheads:
                #    result += tikz_draw_edge(multihead, child, graph_link.getEdge(multihead, child), "below", "thick", "orange")
                #    graph_link.deleteEdge(multihead,child)
                    
            
            elif child in graph_link.table and head in graph_link.table[child]:
                result += tikz_draw_edge(child, head, graph_link.getEdge(child,head), "below", "ultra thick")
                result += tikz_draw_edge(head, child, label, "above", "thick")
                graph_link.deleteEdge(child,head)
            
            else:
                result += tikz_draw_edge(head, child, label, "above", "densely dotted")



    for head in graph_link.table:
        children = graph_link.table[head]
        for child in children:
            label = graph_link.labels[(head,child)]
            
            if len(graph_link.heads[child]) > 1 :
                result += tikz_draw_edge(head,child,label, "below", "ultra thick", "orange")
            else:
                result += tikz_draw_edge(head,child,label, "below", "densely dotted")

        
    result += "\t\\end{dependency}\n"

    if subfigure:
        result += "\\end{subfigure}\n"

    return result



# Returns a string that will draw a single edge. 
def tikz_draw_edge(parent, child, label, side, style = None, color = None):
    result = "\t\t\\"

    if color == None:
        color = "blue"
        if side == "below":
            color = "red"

    edgeStyle = "edge style = {"+color
    if style != None:
        edgeStyle += ", "+style+"}"
    else:
        edgeStyle += "}"

    edgeParams = "[edge "+side+", "+edgeStyle+"]"


    # Root
    if parent == "0":
        result += "deproot"+edgeParams+"{"+child+"}{"+label+"}\n"
    # Any other edge
    else:
        result += "depedge"+edgeParams+"{"+parent+"}{"+child+"}{"+label+"}\n"
    return result
