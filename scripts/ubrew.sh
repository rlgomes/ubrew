# this script must run on bash, zsh and sh at minimum

export UBREW_VERSION=0.1
export UBREW_BASEDIR=$HOME/.ubrew/apps/python/3.3.1/bin/

__ubrew_run() {
    (PYTHONPATH=$UBREW_BASEDIR/../lib/python3.3/site-packages:$PYTHONPATH ; 
    $UBREW_BASEDIR/python -m ubrew.cli $@)
}

__ubrew_deactivate() {
    __ubrew_run $@ > /tmp/$$-deactivate.out
    RC=$?
    if [ $RC = 0 ]
    then
        eval VERSION=\${UBREW_$2}

        if [ "$3" = "$VERSION" ]
        then
            unset UBREW_$2
        fi

        for P in `cat /tmp/$$-deactivate.out`; do
            VARIABLE=`echo $P | awk -F= '{print $1}'`
            VALUE=`echo $P | awk -F= '{print $2}'`

            eval CVALUE=\$$VARIABLE
            NEWVALUE=`echo $CVALUE | sed 's/"$VALUE"://g'`
            export $VARIABLE=$NEWVALUE
        done
        echo "deactivated $2 $3"
    else
        return $RC
    fi
}

__ubrew_activate() {
    __ubrew_run $@ > /tmp/$$-activate.out
    RC=$?
    if [ $RC = 0 ]
    then
        eval VERSION=\${UBREW_$2}
        
        if [ "$VERSION" != "" ]
        then
            __ubrew_deactivate deactivate $2 $VERSION
        fi
       
        # store the previous app version activated 
        export UBREW_$2=$3

        for P in `cat /tmp/$$-activate.out`
        do
            VARIABLE=`echo $P | awk -F= '{print $1}'`
            NEWVALUE=`echo $P | awk -F= '{print $2}'`
            OLDVALUE=`eval echo $"$VARIABLE"`
            eval VALUE=\$$VARIABLE
            export $VARIABLE=$NEWVALUE:$VALUE
        done
        echo "activated $2 $3"
    else
        return $RC
    fi
}

ubrew() {
    # this is the command that everyone runs since this function will be 
    # exported so its always visible
    case $1 in
        activate) __ubrew_activate $@ ;;
        deactivate) __ubrew_deactivate $@ ;;
        *) __ubrew_run "$@" ;;
    esac        
}

