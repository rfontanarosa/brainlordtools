#!/bin/bash

USER="clomax"
DB="resources/ys3/db/ys3.db"
SOURCE="resources/ys3/roms/Ys III - Wanderers from Ys (U) [!].smc"
DESTINATION="resources/ys3/roms/Ys III - Wanderers from Ys (I) [!].smc"
TABLE1="resources/ys3/tables/Ys III - Wanderers from Ys (U) [!].tbl"
TABLE2="resources/ys3/tables/Ys III - Wanderers from Ys (U) [!].tbl"

python _ys3.py --crc32check --dump -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
#python _ys3.py --insert -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
