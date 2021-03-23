#!/bin/bash

RESOURCE_PATH="../../brainlordresources/ruinarm"

USER="clomax"
DB="$RESOURCE_PATH/db/ruinarm.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Ruin Arm (J).sfc"

TABLE1="$RESOURCE_PATH/tables/ruin_arm_utf8.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"

python3 ../brainlordtools/ruinarm.py dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
