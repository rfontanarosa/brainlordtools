#!/bin/bash

GAME_ID="brandish2"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.db"
SOURCE="$RESOURCE_PATH/roms/Brandish 2 (U) [!].smc"
DESTINATION="$RESOURCE_PATH/roms/Brandish 2 (I) [!].smc"

TABLE1="$RESOURCE_PATH/tables/Brandish 2 (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Brandish 2 (I) [!].tbl"

DUMP_PATH="$RESOURCE_PATH/dump"

python "$TOOLS_PATH/_utils.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1

python "$TOOLS_PATH/brandish2.py" dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
# python "$TOOLS_PATH/brandish2.py" insert -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -db "$DB" -u "$USER"
