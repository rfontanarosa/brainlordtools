#!/bin/bash

BRAINLORD_PATH="/Users/robertofontanarosa/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/bof2"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/bof2.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Breath of Fire II (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Breath of Fire II (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/Breath of Fire II (U) [!].tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

python "$TOOLS_PATH/_utils.py" file_copy -s "$SOURCE" -d "$DESTINATION"

python "$TOOLS_PATH/bof2.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
# python "$TOOLS_PATH/bof2.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
# python "$TOOLS_PATH/bof2.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

# python "$TOOLS_PATH/bof2.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"