#!/usr/bin/python

class graph:
    """An adjacency list data structure for graphs"""
    def __init__(self):
        self.table = {}
        self.labels = {}
        self.heads = {}
        self.sentence = []
        self.POS_sequence = []

    # Adds an edge to the graph
    def addEdge(self, a, b, label):
        self.table[a] = self.table.get(a, [])
        self.heads[b] = self.heads.get(b, [])

        if b not in self.table[a]:
            self.table[a].append(b)
            self.heads[b].append(a)

        self.labels[(a,b)] = label

    # Checks if an edge exists in our graph
    def existsEdge(self, a, b):
        if self.table.get(a,None) == None:
            return False
        edgeList = self.table[a]
        return b in edgeList

    # Gets an edge in the graph, returning the label or None.
    def getEdge(self, a, b):
        return self.labels.get((a,b),None)

    # Delete an edge
    def deleteEdge(self, a, b):
        if self.getEdge(a, b):
            self.table[a].remove(b)
            if not self.table[a]:
                del self.table[a]

            # I took out the removal of the corresponding head. I needed it to find multiheadedness
            #self.heads[b].remove(a)
            #if not self.heads[b]:
            #    del self.heads[b]

            del self.labels[(a,b)]

    # Populate a graph by reading in conll data
    def readConll(self, conlls):
        for conll in conlls:
            conll = conll.split()
            
            index = conll[0]
            heads = conll[6].split(",")
            labels = conll[7].split(",")

            for head,label in zip(heads, labels):
                if head == "-":
                    continue
                self.addEdge(head, index, label)


            POS = conll[3]
            POS = POS.strip("$")
            self.POS_sequence.append(POS)

            word = conll[1]
            self.sentence.append(word)




# Get a graph from conll data
def getGraph(conll):
    g = graph()
    g.readConll(conll)
    return g

