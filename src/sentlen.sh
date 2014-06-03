#!/bin/bash
# Makes a file that maps every sentence ID to that sentence's length.
cat /tmp/LinksToDAG_links.txt | perl -ne 'chomp; @f = split(", *"); $len{$f[4]}=$f[0] if $len{$f[4]}<$f[0]; $len{$f[4]}=$f[1] if $len{$f[4]}<$f[1]; END { for $sent (keys %len) { print "$sent, $len{$sent}\n"; } }' > /tmp/LinksToDAG_sentlen.txt
