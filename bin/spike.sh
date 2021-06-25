#!/bin/bash

RESOURCE_PATH="../../brainlordresources/spike"

USER="clomax"
DB="$RESOURCE_PATH/db/spike.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Twisted Tales of Spike McFang, The (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Twisted Tales of Spike McFang, The (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/Twisted Tales of Spike McFang, The (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Twisted Tales of Spike McFang, The (U) [!].tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"

python ../brainlordtools/spike.py expand -s "$SOURCE" -d "$DESTINATION"

python ../brainlordtools/spike.py dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"

# python ../brainlordtools/spike.py insert -d "$DESTINATION" -t2 "$TABLE2" -db "$DB" -u "$USER"
