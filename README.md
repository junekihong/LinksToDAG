LinksToDAG
==========

Convert Link Parses to a DAG



Software Dependencies
---------------------

* Install the link grammar parser

Download the source at http://www.abisource.com/projects/link-grammar/

./configure --prefix=/home/user/link-grammar/; make; make install; ldconfig

add the binary in the link-grammar/bin directory to the PATH environment variable, or make a symbolic link using ln -s.

* Install SCIP.

Download from http://scip.zib.de/download.php?fname=scipoptsuite-3.1.0.tgz

make

Add the binary to the PATH enviornment variable, or use a symbolic link.

If make does not run because it cannot find the GMP libraries, then you will need to install those as well

SCIP relies on GMP in order to read ZIMPL programs.

* Install GMP

**With sudo:**

sudo apt-get install libgmp10

**Without sudo:**

download source from https://gmplib.org/ 

./configure --prefix=/home/user/gmp/; make; make check

You will need to add the include and lib directories.

export C_PATH=$C_PATH:/home/user/gmp/include 

export LIBRARY_PATH=/home/user/gmp/lib


* Install Graphviz

Optionally, our program can output all of the link parses into graphviz dotfile to be viewed as a graph.

sudo apt-get install graphviz


Directories
-----------
* src contains the source files

* doc contains the paper

* data contains some sample data.


