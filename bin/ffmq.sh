#!/bin/bash

RESOURCE_PATH="../../brainlordresources/ffmq"

USER="clomax"
SOURCE="$RESOURCE_PATH/roms/Final Fantasy - Mystic Quest (U) (V1.1).sfc"
DESTINATION="$RESOURCE_PATH/roms/Final Fantasy - Mystic Quest (I) (V1.1).sfc"
TABLE1="$RESOURCE_PATH/tables/ffmq.tbl"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

python ../brainlordtools/ffmq.py dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"
python ../brainlordtools/ffmq.py insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE1" -tp "$TRANSLATION_MISC_PATH"
