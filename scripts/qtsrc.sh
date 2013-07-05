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
        # ~/.ackrc: --type-set=qml=.qml
        ack --ignore-dir=doc --ignore-dir=3rdparty -f --type=cpp --type=js --type=qml src > $outpath/$d.files
        cd ..
    fi
done
