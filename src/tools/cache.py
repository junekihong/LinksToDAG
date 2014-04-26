#!/usr/bin/env python

import pickle
import os

class cache:
    """ Keeps track of which sentences we have already parsed.
    Will try to cache the parses of the sentences
    Will output all of the parses to a given file."""
    
    def __init__(self, cacheLocation="/tmp/LinksToDAG_cache.p"):
        self.cache = {}
        self.cacheLocation = cacheLocation
        self.load()
    
    # Save the cache. Pickle the dict to a file.
    def save(self):
        pickle.dump(self.cache, open(self.cacheLocation, "wb"))

    # Load the cache. Load the pickled dict.
    def load(self):
        #Check if the file exists. Create it if it doesn't
        if not os.path.exists(self.cacheLocation):
            self.save()
            #    open(self.cacheLocation, 'w').close()

        self.cache = pickle.load(open(self.cacheLocation,"rb"))

    # Clear the cache.
    def clear(self):
        self.cache = {}

    # Store a value.
    def store(self,key, value):
        self.cache[key] = value
        
    # Get a value.
    def get(self,key):
        return self.cache[key]

    # Check for a value.
    def check(self,key):
        return self.cache.get(key,None) != None



if __name__=="__main__":
    c = cache()
    c.saveCache()
    c.loadCache()

