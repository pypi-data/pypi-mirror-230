#!/bin/sh

SRC=../../pixmaps/chrysalide-logo.svg

for sz in 8 16 22 24 32 36 42 48 64 72 96 128 192 256 512;
do

    DIR="${sz}x${sz}"

    rm -rf $DIR

    mkdir $DIR

    inkscape -z -w $sz -h $sz $SRC -e $DIR/chrysalide.png 1> /dev/null 2> /dev/null

    echo "icons${sz}dir = \$(DESKTOP_DATADIR)/icons/hicolor/$DIR/apps"
    echo "icons${sz}_DATA = $DIR/chrysalide.png"
    echo ""

done
