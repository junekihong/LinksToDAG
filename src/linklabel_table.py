#!/usr/bin/env python

# a hard coded table for a temporary mock-up solver.
# This was used to help prototype the project pipeline.

#label table
lt = {}

# True is left, False is right
lt["WV"] = False
lt["Wi"] = False
lt["CO"] = True
lt["Wd"] = False
lt["Op"] = False
lt["Sp"] = True
lt["Dmcn"] = True
lt["Ifd"] = True
lt["Bp"] = True
lt["TO"] = False
lt["R"] = True
lt["Ix"] = True
lt["RS"] = True
lt["IV"] = False
lt["Pg*b"] = False
lt["E"] = True
lt["Pv"] = False
lt["Opm"] = False
lt["MVp"] = False
lt["Jp"] = False
lt["AN"] = True
lt["CC"] = False
lt["Ss"] = True



# Returns true or false depending on which way the dependency should go.
def childParentLookup(node1, node2, label):
    return lt.get(label,None)
