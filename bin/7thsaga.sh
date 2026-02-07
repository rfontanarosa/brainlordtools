#!/bin/bash

GAME_ID="7thsaga"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/7th Saga, The (U) [!] - decompressed.sfc"
DESTINATION="$RESOURCE_PATH/roms/7th Saga, The (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/7th Saga, The (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/7th Saga, The (U) [!].tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

python "$TOOLS_PATH/_utils.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1
python "$TOOLS_PATH/_utils.py" copy_file -s "$SOURCE" -d "$DESTINATION"

python "$TOOLS_PATH/7thsaga.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/7thsaga.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python "$TOOLS_PATH/7thsaga.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/7thsaga.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
python "$TOOLS_PATH/7thsaga.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
python "$TOOLS_PATH/7thsaga.py" insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -tp "$TRANSLATION_MISC_PATH"
