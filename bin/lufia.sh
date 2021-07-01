#!/bin/bash

BRAINLORD_PATH="/Users/rfontanarosa/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/lufia"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/lufia.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Lufia & The Fortress of Doom (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Lufia & The Fortress of Doom (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/AllOriginal.tbl"
TABLE2="$RESOURCE_PATH/tables/LufiaScriptIta.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

python "$TOOLS_PATH/lufia.py" file_copy -s "$SOURCE" -d "$DESTINATION"
python "$TOOLS_PATH/lufia.py" expand -d "$DESTINATION"

python "$TOOLS_PATH/lufia.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/lufia.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python "$TOOLS_PATH/lufia.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/lufia.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
python "$TOOLS_PATH/lufia.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
python "$TOOLS_PATH/lufia.py" insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE1" -tp "$TRANSLATION_MISC_PATH"

asar "$RESOURCE_PATH/hack/hack.asm" "$DESTINATION"
