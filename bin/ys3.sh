#!/bin/bash

GAME_ID="ys3"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
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

python "$MANAGER_PATH/manager.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1
python "$MANAGER_PATH/manager.py" copy_file -s "$SOURCE" -d "$DESTINATION" || exit 1

python "$TOOLS_PATH/ys3.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/ys3.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python "$TOOLS_PATH/ys3.py" dump_misc -s "$SOURCE" -t1 "$TABLE3" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/ys3.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
# python "$TOOLS_PATH/ys3.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
