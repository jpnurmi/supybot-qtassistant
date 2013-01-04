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
        ack --ignore-dir=doc --ignore-dir=3rdparty -f --type=cpp src > $outpath/$d.files
        ctags --fields=Kns --languages=C++ --exclude=3rdparty --exclude=doc --recurse=yes -f $outpath/$d.tags src
        cd ..
    fi
done
