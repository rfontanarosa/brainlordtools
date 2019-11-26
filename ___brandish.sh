#!/bin/bash

USER="clomax"
DB="./resources/brandish/db/brandish.db"
SOURCE="./resources/brandish/roms/Brandish (U) [!].smc"
DESTINATION="./resources/brandish/roms/Brandish (I) [!].smc"
TABLE1="./resources/brandish/tables/Brandish (U) [!].tbl"
TABLE2="./resources/brandish/tables/Brandish (I) [!].tbl"

python _brandish.py --crc32check --dump -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
#python _brandish.py --insert -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
