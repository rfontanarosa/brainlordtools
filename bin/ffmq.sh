#!/bin/bash

GAME_ID="ffmq"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Final Fantasy - Mystic Quest (U) (V1.1).sfc"
# DESTINATION="$RESOURCE_PATH/roms/Final Fantasy - Mystic Quest (I) (V1.1).sfc"
DESTINATION="$BRAINLORD_PATH/Final-Fantasy-Mystic-Quest-ITA/ffmq_new.sfc"

TABLE1="$RESOURCE_PATH/tables/ffmq.tbl"

DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

python "$TOOLS_PATH/_utils.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1

python "$TOOLS_PATH/ffmq.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/ffmq.py" insert_misc -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE1" -tp "$TRANSLATION_MISC_PATH"
