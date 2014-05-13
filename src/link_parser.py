#!/usr/bin/python

from tools.cache import *
from tools.iterview import *
from subprocess import *
from pprint import pprint
import subprocess, sys, os


class linkParser:
    """ Will call the link-parser on a sentence and output the result"""
    
    def __init__(self, lang = "en"):
        self.cache = cache("/tmp/LinksToDAG_linkparses_cache.p")
        self.language = lang

    def parse_all(self,sentences, outputFile = "/tmp/LinksToDAG_linkparses.txt"):
        output = open(outputFile, "wb")

        # Thanks to Tim Vieira and his arsenal for this neat loading bar visualization.
        for x in iterview(xrange(len(sentences)), msg='Sentences Processed',every=1):
            sentence = sentences[x].strip()

            if self.language != "en":
                ID = sentence + "#" + self.language
            else:
                ID = sentence

            # In the cache
            if self.cache.check(ID): 
                parse = self.cache.get(ID)
            # Not in the cache
            else:
                parse = self.parse(sentence)
                self.cache.store(ID,parse)

            print parse

            output.write(parse)
        output.close()

        
    def closeParser(self):
        self.cache.save()

    def parse(self,sentence):
        echo_process = Popen(["echo",sentence], stdout=PIPE)
        linkparser_process = Popen(["link-parser", self.language, "-!graphics=0", "-!links=0", "-!echo=1", "-!postscript=1", "-!panic=0"], stdin=echo_process.stdout, stdout=PIPE, stderr=subprocess.PIPE)
        echo_process.stdout.close()

        output, err = linkparser_process.communicate()        
        linkparser_process.stdout.close()
        return output


if __name__ == "__main__":
    if len(sys.argv) > 3:
        language = sys.argv[3]
        parser = linkParser(language)
    else:
        parser = linkParser()

    inputfile = open(sys.argv[1], "rb")
    sample = -1
    

    if len(sys.argv) > 2:
        sample = int(sys.argv[2])

    if sample == -1:
        sentences = inputfile.readlines()
    else:
        sentences = inputfile.readlines()[:sample]    


    
    parser.parse_all(sentences)

    inputfile.close()
    parser.closeParser()
    
