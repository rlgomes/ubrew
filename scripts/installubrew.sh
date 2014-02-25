#!/bin/bash
#
# Install bash script that can install ubrew on any *nix system
#
# The default behaviour is to download and install Python-3.3.1 in the ~/.ubrew
# to gaurantee you're installing ubrew in a way that it can count on using 
# Python-3.3.1 to run itself.
# 

UBREW_GIT_SOURCE="git://github.com/rlgomes/ubrew#egg=ubrew"
PYTHON_INSTALL="$HOME/.ubrew/apps/python/3.3.1"
TEMP="/tmp"
DOWNLOAD_FILENAME=""

function run() 
{
    echo "$1"
    $2
    if [ $? != 0 ]
    then
        echo $3
        exit -1
    fi
}

if [ `uname` == 'Linux' ]
then

    if [ -e /etc/debian_version ]
    then
        # debian
        yes | sudo apt-get install build-essential libsqlite3-dev bzip2 libbz2-dev g++ autoconf git-core
    elif [ -e /bin/yum ]
    then
        # redhat
        yum install openssl-devel readline-devel sqlite-devel
    fi 
    
    DOWNLOAD_FILENAME="Python-3.3.1.tgz"
    DOWNLOAD="http://www.python.org/ftp/python/3.3.1/$DOWNLOAD_FILENAME"
    OUTPUT_DIRECTORY="$TEMP/ubrew/python"
    mkdir -p $OUTPUT_DIRECTORY

    if [ ! -e $PYTHON_INSTALL ]
    then

        run "Downloading Python Source" \
            "curl -# -L $DOWNLOAD -o $TEMP/$DOWNLOAD_FILENAME" \
            "Failed to download Python Source"

        cp $TEMP/$DOWNLOAD_FILENAME $OUTPUT_DIRECTORY/$DOWNLOAD_FILENAME

        cd $OUTPUT_DIRECTORY
        run "Uncompressing Python 3.3.1" \
            "tar xvfz $DOWNLOAD_FILENAME" \
            "Failed to uncompress Python 3.3.1"

        cd Python-3.3.1
        run "Configuring Python 3.3.1" \
            "./configure --prefix=$PYTHON_INSTALL" \
            "Failed to configure Python 3.3.3"

        run "Building Python 3.3.1"\
            "make" \
            "Failed to build Python 3.3.1"

        run "Installing Python 3.3.1" \
            "make install" \
            "Failed to install Python 3.3.1"

        ln -sf $PYTHON_INSTALL/bin/python3 $PYTHON_INSTALL/bin/python
    else
        echo "Python 3.3.1 already installed at $PYTHON_INSTALL"
    fi

    PATH=$PYTHON_INSTALL/bin:$PATH
    PYTHONPATH=$PYTHON_INSTALL/lib/python4.3/site-packages/:$PYTHONPATH
   
    if [ ! -e $PYTHON_INSTALL/bin/easy_install ]
    then 
        mkdir -p $TEMP/ubrew/setuptools
        cd $TEMP/ubrew/setuptools
        run "Downloading setuptools source" \
            "curl -# https://pypi.python.org/packages/source/s/setuptools/setuptools-2.1.tar.gz -o $OUTPUT_DIRECTORY/setuptools-2.1.tar.gz" \
            "Failed to download setuptools source"
    
        cd $OUTPUT_DIRECTORY
        run "Uncompressing Setuptools" \
            "tar xvfz setuptools-2.1.tar.gz" \
            "Failed to uncompress setuptools "

        cd setuptools-2.1
        run "Building & Installing setuptools" \
            "$PYTHON_INSTALL/bin/python3 setup.py install" \
            "Failed to build & install setuptools"
    else
        echo "setuptools already installed"
    fi

    run "Installing pip" \
        "easy_install pip" \
        "Failed to install pip"
    
    run "Installing ubrew" \
        "pip install -e $UBREW_GIT_SOURCE" \
        "Failed to install ubrew"

    echo "********************************************************************"
    echo "*"
    echo "* ubrew is now installed and you can enable it by sourcing the "
    echo "* ubrew.sh scirpt like so: "
    echo "*"
    echo "* source $PYTHON_INSTALL/bin/ubrew.sh"
    echo "*"
    echo "* If you put the above source line in your .bashrc or .bash_profile"
    echo "* file you can have ubrew always available "
    echo "*"
    echo "********************************************************************"

elif [ `uname` == 'Darwin' ]
then
    DOWNLOAD_FILENAME="Python-3.3.1-macosx10.6.dmg"
    DOWNLOAD="http://www.python.org/ftp/python/3.3.1/$DOWNLOAD_FILENAME"
    OUTPUT_DIRECTORY="$TEMP/$$_ubrew/python"
    mkdir -p $OUTPUT_DIRECTORY

    #curl -X GET $DOWNLOAD -o $OUTPUT_DIRECTORY/$DOWNLOAD_FILENAME -C - 2>&1 
    curl -X GET $DOWNLOAD -o $TEMP/$DOWNLOAD_FILENAME -C - 2>&1 

    cp $TEMP/$DOWNLOAD_FILENAME $OUTPUT_DIRECTORY/$DOWNLOAD_FILENAME


else    
    echo "Unsupported OS"
    exit -1   
fi


