#!/bin/bash

BRAINLORD_PATH="/Users/rfontanarosa/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/gaia"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/gaia.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Illusion of Gaia (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Illusion of Gaia (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/Illusion of Gaia (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Illusion of Gaia (U) [!].tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"

python "$TOOLS_PATH/gaia.py" file_copy -s "$SOURCE" -d "$DESTINATION"
# python "$TOOLS_PATH/gaia.py" expand -d "$DESTINATION"

python "$TOOLS_PATH/gaia.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
