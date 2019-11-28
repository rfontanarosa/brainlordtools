#!/bin/bash

RESOURCE_PATH="./resources/neugier"

USER="clomax"
DUMP_PATH="$RESOURCE_PATH/dump"
DB="$RESOURCE_PATH/db/neugier.db"
SOURCE="$RESOURCE_PATH/roms/Neugier (J) [T+Eng2.00_Haeleth&RPGOne].sfc"
DESTINATION="$RESOURCE_PATH/roms/Neugier - Umi to Kaze no Kodou (I).sfc"
TABLE1="$RESOURCE_PATH/tables/Neugier - Umi to Kaze no Kodou (U).tbl"
TABLE2="$RESOURCE_PATH/tables/Neugier - Umi to Kaze no Kodou (I).tbl"

python ../brainlordtools/neugier.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
#python ../brainlordtools/neugier.py insert -d "$DESTINATION" -t2 "$TABLE2" -db "$DB" -u "$USER"
