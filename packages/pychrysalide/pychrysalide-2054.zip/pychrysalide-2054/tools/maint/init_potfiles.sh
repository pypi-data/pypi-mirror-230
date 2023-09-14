#!/bin/bash

function keep_i18n() {

    while read file;
    do

        if [ "$file" != "i18n.h" ]; then

            grep -q '_(' $file

            status=$?

            if [ "$status" -eq 0 ]; then
                echo $file
            fi

        fi

    done

}

mkdir -p po

find . -type f -name '*.[ch]' | keep_i18n | sort >  po/POTFILES.in
