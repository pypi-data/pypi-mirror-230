#!/bin/sh

python3 ./palette.py

python3 ./expand.py
python3 ./expand.py --dark

python3 ./collapse.py
python3 ./collapse.py --dark
