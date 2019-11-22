#!/bin/bash

USER="clomax"
DB="resources/brandish2/db/brandish2.db"
SOURCE="resources/brandish2/roms/Brandish 2 (U) [!].smc"
DESTINATION="resources/brandish2/roms/Brandish 2 (I) [!].smc"
TABLE1="resources/brandish2/tables/Brandish 2 (U) [!].tbl"
TABLE2="resources/brandish2/tables/Brandish 2 (I) [!].tbl"

python2 _brandish2.py --crc32check --dump -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
#python2 _brandish2.py --insert -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
