#!/bin/bash

RESOURCE_PATH="../resources/bof/gba"

DUMP_PATH="$RESOURCE_PATH/dump"
SOURCE="$RESOURCE_PATH/roms/0245 - Breath of Fire (I).gba"
TABLE1="$RESOURCE_PATH/tables/0245 - Breath of Fire (U).tbl"

python ../brainlordtools/bof-gba.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH"
