LinksToDAG
==========

Convert Link Parses to a DAG

Software Dependencies
---------------------

Install the link grammar parser
* If you have sudo
** sudo apt-get install link-grammar
* If you don't have sudo
** Download the source at http://www.abisource.com/projects/link-grammar/
** configure --prefix=/home/user/link-grammar/, make, make install
** add the binary in the link-grammar/bin directory to the PATH environment variable, or make a symbolic link using ln -s.

Install SCIP.
* Download from http://scip.zib.de/download.php?fname=scipoptsuite-3.1.0.tgz
* make
* add the binary to the PATH enviornment variable, or use a symbolic link.
* If make does not run because it cannot find the GMP libraries, then you will need to install those as well
** with sudo: sudo apt-get install libgmp10
** without sudo: download source from https://gmplib.org/ 
./configure --prefix=/home/user/gmp/, make, make check
*** You will need to add the include and lib directories.
export CPLUS_INCLUDE_PATH=$CPLus_INCLUDE_PTH:/home/user/gmp/include 
export LIBRARY_PATH=/home/user/gmp/lib


Install Graphviz
sudo apt-get install graphviz


Directories
-----------
* src contains the source files

* doc contains the paper

* data contains some sample data.


