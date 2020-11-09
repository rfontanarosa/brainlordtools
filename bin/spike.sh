#!/bin/bash

RESOURCE_PATH="../../brainlordresources/spike"

USER="clomax"
DUMP_PATH="$RESOURCE_PATH/dump"
DB="$RESOURCE_PATH/db/spike.db"
SOURCE="$RESOURCE_PATH/roms/Twisted Tales of Spike McFang, The (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Twisted Tales of Spike McFang, The (I) [!].sfc"
TABLE1="$RESOURCE_PATH/tables/Twisted Tales of Spike McFang, The (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Twisted Tales of Spike McFang, The (U) [!].tbl"

python ../brainlordtools/spike.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
#python ../brainlordtools/spike.py insert -d "$DESTINATION" -t2 "$TABLE2" -db "$DB" -u "$USER"
