#!/bin/sh

if [ -z "$ARM_CROSS" ]; then
    echo "ARM_CROSS is not set!"
    exit 1
fi

LANG=C python3 -m unittest discover -v -p '*py'
