#!/bin/bash

SOURCE="./resources/bof/gba/roms/0245 - Breath of Fire (I).gba"
TABLE1="./resources/bof/gba/tables/0245 - Breath of Fire (U).tbl"

python _bof-gba.py --dump -s "$SOURCE" -t1 "$TABLE1"
