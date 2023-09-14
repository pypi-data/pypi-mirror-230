#!/bin/sh

MAX_FORMATS=20

export PYTHONPATH=$(readlink -f "$PWD/../../plugins/pychrysa/.libs")

if [ ! -e "$PYTHONPATH/pychrysalide.so" ]; then
    echo '[!] PyChrysalide module not found, exiting...'
    exit 1
else
    echo "[i] PyChrysalide module found in $PYTHONPATH."
fi

which melkor 2>&1 > /dev/null

if [ "$?" -ne 0 ]; then
    echo '[!] melkor not found, exiting...'
    exit 1
else
    echo '[i] melkor found!'
fi

if [ -z "$FFUZZ_TEMPLATE" ]; then
    echo '[!] $FFUZZ_TEMPLATE is not set, exiting...'
    exit 1
else
    echo "[i] Using $FFUZZ_TEMPLATE as template."
fi

WORKING_DIR="orcs_$(basename $FFUZZ_TEMPLATE)"
rm -rf $WORKING_DIR

melkor -A -n $MAX_FORMATS -l 15 -q $FFUZZ_TEMPLATE

ulimit -c unlimited

cd $WORKING_DIR

chmod a+x *
chmod a-x Report_*

core_count=0

for f in `find . -type f -perm +111`; do

    target=`basename $f`

    echo "[*] Processing '$WORKING_DIR/$target'..."

    python3-dbg ../process.py $target > /dev/null

    if [ "$?" -eq 0 ]; then
        echo '  --> disassembly done!'
    fi

    if [ -e core ]; then
        echo '  --> renaming core...'
        mv core $target.core
        core_count=$((core_count + 1))
    fi

done

echo '[i] Done.'

echo "[i] Got $core_count core(s) for $MAX_FORMATS input files."
