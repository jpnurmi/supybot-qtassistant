#!/bin/bash

outpath=`pwd`

if [ ! -d "$1" ]; then
    echo "Usage: `basename $0` <path/to/qt5>"
    exit 1
fi

cd $1
for d in qt*; do
    if [ -d $d/src ]; then
        echo $d
        cd $d
        # ~/.ackrc:
        #--type-set=mm=.mm
        #--type-set=qml=.qml
        ack --ignore-dir=doc --ignore-dir=3rdparty -f --type=cpp --type=js --type=qml --type=mm src > $outpath/$d.files
        cd ..
    fi
done
