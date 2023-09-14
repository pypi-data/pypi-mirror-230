#!/bin/bash

GITCMD="git log --pretty=format:%ad --date=format:%Y "

function get_min_date()
{
    $GITCMD $1 | tail -1
}

function get_max_date()
{
    $GITCMD $1 | head -1
}

function process_c_file()
{
    filename=$1

    echo "Processing $filename..."

    min=$( get_min_date $filename )

    max=$( get_max_date $filename )

    if [ "$min" -eq "$max" ]; then
        timestamp="$min"
    else
        timestamp="$min-$max"
    fi

    sed -i "s# \* Copyright (C) [0-9-]* Cyrille Bagard# \* Copyright (C) $timestamp Cyrille Bagard#" $filename

}


if [ ! -f configure.ac ]; then
    echo "This script has to be run from the top directory."
    exit 1
fi

for file in $( find . -name '*.[ch]' -exec grep -l 'Copyright.*Cyrille Bagard$' {} \; );
do
    git ls-files --error-unmatch $file > /dev/null 2>&1 \
        && process_c_file $file

done
