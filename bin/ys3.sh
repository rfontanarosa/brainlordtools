#!/bin/bash

BRAINLORD_PATH="/Users/rfontanarosa/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/ys3"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/ys3.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Ys III - Wanderers from Ys (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Ys III - Wanderers from Ys (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/Ys III - Wanderers from Ys (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Ys III - Wanderers from Ys (U) [!].tbl"
TABLE3="$RESOURCE_PATH/tables/Ys III - Wanderers from Ys (U) [!].other.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

python "$TOOLS_PATH/_utils.py" file_copy -s "$SOURCE" -d "$DESTINATION"

python "$TOOLS_PATH/ys3.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/ys3.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python "$TOOLS_PATH/ys3.py" dump_misc -s "$SOURCE" -t1 "$TABLE3" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/ys3.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
# python "$TOOLS_PATH/ys3.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
