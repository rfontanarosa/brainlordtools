#!/bin/bash

GAME_ID="ignition"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Ignition Factor, The (U).sfc"
DESTINATION="$RESOURCE_PATH/roms/Ignition Factor, The (I).sfc"

TABLE1="$RESOURCE_PATH/tables/Ignition Factor, The (U).tbl"
TABLE2="$RESOURCE_PATH/tables/Ignition Factor, The (U).tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

python "$TOOLS_PATH/_utils.py" file_copy -s "$SOURCE" -d "$DESTINATION"

python "$TOOLS_PATH/ignition.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"

python "$TOOLS_PATH/ignition.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE1" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"

if ! command -v asar &> /dev/null
then
  echo "Command 'asar' not found."
  exit
else
  asar "$RESOURCE_PATH/asm/main.asm" "$DESTINATION"
fi
