#!/bin/bash

RESOURCE_PATH="../../brainlordresources/7thsaga"

USER="clomax"
DB="$RESOURCE_PATH/db/7thsaga.sqlite3"
SOURCE="$RESOURCE_PATH/roms/7th Saga, The (U) [!] - decompressed.sfc"
DESTINATION="$RESOURCE_PATH/roms/7th Saga, The (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/7th Saga, The (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/7th Saga, The (U) [!].tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
# TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

python3 ../brainlordtools/7thsaga.py dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
python3 ../brainlordtools/7thsaga.py dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python3 ../brainlordtools/7thsaga.py dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

# python3 ../brainlordtools/7thsaga.py insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
python3 ../brainlordtools/7thsaga.py insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
# python3 ../brainlordtools/7thsaga.py insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -tp "$TRANSLATION_MISC_PATH"

# asar "$RESOURCE_PATH/hack/main.asm" "$DESTINATION"
