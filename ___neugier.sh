#!/bin/bash

USER="clomax"
DB="./resources/neugier/db/neugier.db"
SOURCE="./resources/neugier/roms/Neugier (J) [T+Eng2.00_Haeleth&RPGOne].sfc"
DESTINATION="./resources/neugier/roms/Neugier - Umi to Kaze no Kodou (I).sfc"
TABLE1="./resources/neugier/tables/Neugier - Umi to Kaze no Kodou (U).tbl"
TABLE2="./resources/neugier/tables/Neugier - Umi to Kaze no Kodou (I).tbl"

python2 _neugier.py --crc32check --dump -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
#python2 _neugier.py --insert -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
