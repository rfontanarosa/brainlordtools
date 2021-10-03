#!/bin/bash

BRAINLORD_PATH="/Users/rfontanarosa/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/spike"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/spike.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Twisted Tales of Spike McFang, The (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Twisted Tales of Spike McFang, The (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/Twisted Tales of Spike McFang, The (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Twisted Tales of Spike McFang, The (U) [!] - 2.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"

CURRENT_PATH=$PWD
WINE_PATH="/Applications/Wine Stable.app/Contents/Resources/wine/bin"
cd "$BRAINLORD_PATH/mcfang-dec"
"$WINE_PATH/wine" "mccmp.exe" "$SOURCE" "$DESTINATION"
cd $CURRENT_PATH

# python "$TOOLS_PATH/spike.py" file_copy -s "$SOURCE" -d "$DESTINATION"
python "$TOOLS_PATH/spike.py" expand -d "$DESTINATION"

python "$TOOLS_PATH/spike.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"

python "$TOOLS_PATH/spike.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE1" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"

asar "$RESOURCE_PATH/asm/main.asm" "$DESTINATION"
