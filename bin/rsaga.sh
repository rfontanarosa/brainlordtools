#!/bin/bash

GAME_ID="rsaga"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Romancing SaGa (U) (V1.2) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Romancing SaGa (I) (V1.0) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/rs.tbl"
TABLE2="$RESOURCE_PATH/tables/rsaga-misc.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATED_TEXT_PATH="$RESOURCE_PATH/translated_text"

python "$MANAGER_PATH/manager.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1
python "$MANAGER_PATH/manager.py" copy_file -s "$SOURCE" -d "$DESTINATION" || exit 1

python "$TOOLS_PATH/rsaga.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/rsaga.py" dump_misc -s "$SOURCE" -t1 "$TABLE2" -dp "$DUMP_MISC_PATH"
python "$TOOLS_PATH/rsaga.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"

python "$TOOLS_PATH/rsaga.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATED_TEXT_PATH" -db "$DB" -u "$USER"