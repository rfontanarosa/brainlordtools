#!/bin/bash

GAME_ID="rsaga"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Romancing SaGa (U) (V1.2) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Romancing SaGa (I) (V1.0) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/rs.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"

python "$MANAGER_PATH/manager.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1
python "$MANAGER_PATH/manager.py" copy_file -s "$SOURCE" -d "$DESTINATION" || exit 1

python "$TOOLS_PATH/rsaga.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"

python "$TOOLS_PATH/rsaga.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"