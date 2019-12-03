#!/bin/bash

RESOURCE_PATH="./resources/brainlord"

USER="clomax"
DUMP_PATH="$RESOURCE_PATH/dump"
DB="$RESOURCE_PATH/db/brainlord.db"
SOURCE="$RESOURCE_PATH/roms/Brain Lord (U) [!].smc"
DESTINATION="$RESOURCE_PATH/roms/Brain Lord (I) [!].smc"
TABLE1="$RESOURCE_PATH/tables/Brain Lord (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Brain Lord (U) [!].tbl"

python _brainlord.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
#python _brainlord.py insert -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -db "$DB" -u "$USER"