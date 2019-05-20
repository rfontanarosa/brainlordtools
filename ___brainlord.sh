#!/bin/bash

USER="clomax"
DB="brainlord/db/brainlord.db"
SOURCE="brainlord/roms/Brain Lord (U) [!].smc"
DESTINATION="brainlord/roms/Brain Lord (I) [!].smc"
TABLE1="brainlord/tables/Brain Lord (U) [!].tbl"
TABLE2="brainlord/tables/Brain Lord (U) [!].tbl"

echo $DB

python _brainlord.py --crc32check --dump -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"