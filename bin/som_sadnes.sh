#!/bin/bash

GAME_ID="som"

source ./_common.sh

USER="sadnes"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Secret of Mana (ITA - SADNESS).sfc"

TABLE1="$RESOURCE_PATH/tables/som_main.tbl"
TABLE3="$RESOURCE_PATH/tables/som_main_with_dte_sadnes.tbl"
TABLE6="$RESOURCE_PATH/tables/som_credits.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/$USER/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/$USER/dump_misc"

python "$MANAGER_PATH/manager.py" crc_check -s "$SOURCE" -g "som_sadnes" || exit 1

python "$TOOLS_PATH/som.py" dump_text -s "$SOURCE" -t1 "$TABLE3" -t2 "$TABLE6" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/som.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"
