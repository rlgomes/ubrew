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

 * Debian:  sudo apt-get install curl git-core 

 * RedHat:  sudo yum install curl git-core 

 * Gentoo:  

Also make sure you have the latest gcc installed on either system (I'll provide
more information on how to get those done for Debian & Redhat systems later).


usage
=====

After installing you can start to use ubrew immediately and its quite easy to 
get a few other versions of python installed like so:

    > ubrew install python 2.7.3

Check which versions are currently available:

    > ubrew available python
        Installable Versions
         * 2.0 2.0.1
         * 2.1 2.1.1 2.1.2 2.1.3
         * 2.2 2.2.1 2.2.2 2.2.3
         * 2.3 2.3.1 2.3.2 2.3.3 2.3.4 2.3.5 2.3.6 2.3.7
         * 2.4 2.4.1 2.4.2 2.4.3 2.4.4 2.4.5 2.4.6
         * 2.5 2.5.1 2.5.2 2.5.3 2.5.4 2.5.5 2.5.6
         * 2.6 2.6.1 2.6.2 2.6.3 2.6.4 2.6.5 2.6.6 2.6.7 2.6.8 2.6.9
         * 2.7 2.7.1 2.7.2 2.7.3 2.7.4 2.7.5 2.7.6
         * 3.0 3.0.1
         * 3.1 3.1.1 3.1.2 3.1.3 3.1.4 3.1.5
         * 3.2 3.2.1 3.2.2 3.2.3 3.2.4 3.2.5
         * 3.3.0 3.3.1 3.3.2 3.3.3 3.3.4
         * 3.4.0
 
Currently there are a few other packages available but not given this is still
an early version of ubrew not everything installs right out of the box. Feel 
free to open any issues found as I'm still trying to figure out a better way to 
detect which versions would install depending on your setup and possibly having
more information on why certain version can't be installed such as details about
missing system level packges.


