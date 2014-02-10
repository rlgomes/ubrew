ubrew
=====

Universal Brew is intended to make it easy to automate the installation of 
various tools, libraries and development tools across all Nix systems. This is
definitely not production ready as I will be making a lot of changes to make
adding new tools, libraries, etc easy and without having to write any code.

installation
============

Windows: **(not supported)**

Mac OS X: **Working on it**

Linux:

> curl -# https://raw.github.com/rlgomes/ubrew/master/scripts/installubrew.sh | bash

This will install ubrew under ~/.ubrew and also make sure to setup python 3.3.1
which is currently the Python runtime used by default when running ubrew.

requirements
============

Linux:

* Debian:  yes | sudo apt-get install curl git-core 

* RedHat:  yes | sudo yum install curl git-core 

Also make sure you have the latest gcc installed on either system (I'll provide
more information on how to get those done for Debian & Redhat systems later).



