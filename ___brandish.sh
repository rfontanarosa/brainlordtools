#!/bin/bash

RESOURCE_PATH="./resources/brandish"

USER="clomax"
DUMP_PATH="$RESOURCE_PATH/dump"
DB="$RESOURCE_PATH/db/brandish.db"
SOURCE="$RESOURCE_PATH/roms/Brandish (U) [!].smc"
DESTINATION="$RESOURCE_PATH/roms/Brandish (I) [!].smc"
TABLE1="$RESOURCE_PATH/tables/Brandish (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Brandish (I) [!].tbl"

python _brandish.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
#python _brandish.py insert -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -db "$DB" -u "$USER"
