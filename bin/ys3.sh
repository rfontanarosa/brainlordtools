#!/bin/bash

RESOURCE_PATH="../resources/ys3"

USER="clomax"
DUMP_PATH="$RESOURCE_PATH/dump"
DB="$RESOURCE_PATH/db/ys3.db"
SOURCE="$RESOURCE_PATH/roms/Ys III - Wanderers from Ys (U) [!].smc"
DESTINATION="$RESOURCE_PATH/roms/Ys III - Wanderers from Ys (I) [!].smc"
TABLE1="$RESOURCE_PATH/tables/Ys III - Wanderers from Ys (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Ys III - Wanderers from Ys (U) [!].tbl"

python ../brainlordtools/ys3.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
python ../brainlordtools/ys3.py insert -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -db "$DB" -u "$USER"
