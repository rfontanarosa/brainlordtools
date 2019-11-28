#!/bin/bash

RESOURCE_PATH="../resources/brandish2"

USER="clomax"
DUMP_PATH="$RESOURCE_PATH/dump"
DB="$RESOURCE_PATH/db/brandish2.db"
SOURCE="$RESOURCE_PATH/roms/Brandish 2 (U) [!].smc"
DESTINATION="$RESOURCE_PATH/roms/Brandish 2 (I) [!].smc"
TABLE1="$RESOURCE_PATH/tables/Brandish 2 (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Brandish 2 (I) [!].tbl"

python ../brainlordtools/brandish2.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
#python ../brainlordtools/brandish2.py insert -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -db "$DB" -u "$USER"
