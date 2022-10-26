#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/brandish"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/brandish.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Brandish (U) [!].smc"
DESTINATION="$RESOURCE_PATH/roms/Brandish (I) [!].smc"

TABLE1="$RESOURCE_PATH/tables/Brandish (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Brandish (I) [!].tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation"

python "$TOOLS_PATH/brandish.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
# python "$TOOLS_PATH/brandish.py" insert_text -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATION_TEXT_PATH" -t2 "$TABLE2" -db "$DB" -u "$USER"

# python "$TOOLS_PATH/brandish.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
# python "$TOOLS_PATH/brandish.py" insert_gfx -d "$DESTINATION" -tp "$TRANSLATION_PATH"
