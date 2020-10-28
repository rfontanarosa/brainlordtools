#!/bin/bash

RESOURCE_PATH="../../brainlordresources/brandish"

USER="clomax"
DUMP_PATH="$RESOURCE_PATH/dump"
TRANSLATION_PATH="$RESOURCE_PATH/translation"
DB="$RESOURCE_PATH/db/brandish.db"
SOURCE="$RESOURCE_PATH/roms/Brandish (U) [!].smc"
DESTINATION="$RESOURCE_PATH/roms/Brandish (I) [!].smc"
TABLE1="$RESOURCE_PATH/tables/Brandish (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Brandish (I) [!].tbl"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

#python ../brainlordtools/brandish.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
python ../brainlordtools/brandish.py insert -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -db "$DB" -u "$USER"
python ../brainlordtools/brandish.py dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python ../brainlordtools/brandish.py insert_gfx -d "$DESTINATION" -tp "$TRANSLATION_PATH"
