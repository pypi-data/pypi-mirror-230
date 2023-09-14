#!/bin/bash

RESET_COLOR="\e[39m"
ERROR_COLOR="\e[91m"


# Check if all Python API definitions end with expected suffixes
function check_python_api_doc_suffix()
{
    filename=$1

    egrep -q '/(pychrysalide|python)/' <<< $filename

    if [ $? -eq 0 ]; then

        for name in $( grep 'PYTHON_METHOD_DEF' $filename | cut -d ' ' -f 2 );
        do

            if [[ "$name" != *_METHOD ]]; then

                echo -e "[!] ${ERROR_COLOR}${filename}${RESET_COLOR}: bad Python method declaration '$name'"

            fi

        done

        for target in "PYTHON_WRAPPER_DEF" "PYTHON_VOID_WRAPPER_DEF" \
                      "PYTHON_FALSE_WRAPPER_DEF" "PYTHON_TRUE_WRAPPER_DEF"; do

            for name in $( grep $target $filename | cut -d ' ' -f 2 );
            do

                if [[ "$name" != *_WRAPPER ]]; then

                    echo -e "[!] ${ERROR_COLOR}${filename}${RESET_COLOR}: bad Python wrapper declaration '$name'"

                fi

            done

        done

        for target in "PYTHON_GETSET_DEF" "PYTHON_CAN_DEF_FULL" "PYTHON_IS_DEF_FULL" "PYTHON_HAS_DEF_FULL" \
                      "PYTHON_RAWGET_DEF_FULL" "PYTHON_GET_DEF_FULL" "PYTHON_GETSET_DEF_FULL"; do

            for name in $( grep $target $filename | cut -d ' ' -f 2 );
            do

                if [[ "$name" != *_ATTRIB ]]; then

                    echo -e "[!] ${ERROR_COLOR}${filename}${RESET_COLOR}: bad Python attribute declaration '$name'"

                fi

            done

        done

        for name in $( grep 'PYTHON_GETTER_WRAPPER_DEF' $filename | cut -d ' ' -f 2 );
        do

            if [[ "$name" != *_ATTRIB_WRAPPER ]]; then

                echo -e "[!] ${ERROR_COLOR}${filename}${RESET_COLOR}: bad Python wrapper declaration '$name'"

            fi

        done

    fi

}


if [ ! -f configure.ac ]; then
    echo "This script has to be run from the top directory."
    exit 1
fi

for file in $( find . -type f -name '*.c' -exec grep -l 'Copyright.*Cyrille Bagard$' {} \; );
do
    check_python_api_doc_suffix $file

done
