#!/bin/bash

RESOURCE_PATH="../resources/soe"

DUMP_PATH="$RESOURCE_PATH/dump"
TRANSLATION_PATH="$RESOURCE_PATH/translation"
SOURCE="$RESOURCE_PATH/roms/evermore.sfc"
DESTINATION="$RESOURCE_PATH/roms/patched_evermore.sfc"
TABLE1="$RESOURCE_PATH/tables/soe.tbl"
MISC1="$RESOURCE_PATH/misc.csv"

python ../brainlordtools/soe.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH"
python ../brainlordtools/soe.py insert -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATION_PATH" -m1 "$MISC1"
