#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/ruinarm"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/ruinarm.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Ruin Arm (J).sfc"
DESTINATION="$RESOURCE_PATH/roms/Ruin Arm (I).sfc"

TABLE1="$RESOURCE_PATH/tables/ruin_arm_utf8.tbl"
TABLE2="$RESOURCE_PATH/tables/ruin_arm_utf8.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"

python "$TOOLS_PATH/ruinarm.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"

python "$TOOLS_PATH/ruinarm.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
