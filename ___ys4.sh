#!/bin/bash

USER="clomax"
DB="./resources/ys4/db/ys4.db"
SOURCE="./resources/ys4/roms/Ys IV - Mask of the Sun (U).sfc"
DESTINATION="./resources/ys4/roms/Ys IV - Mask of the Sun (I).sfc"
TABLE1="./resources/ys4/tables/Ys IV - Mask of the Sun (U).tbl"
TABLE2="./resources/ys4/tables/Ys IV - Mask of the Sun (I).tbl"
TABLE3="./resources/ys4/tables/Ys IV - Mask of the Sun.base.tbl"

#python _ys4.py --mte_finder -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

python _ys4.py --crc32check --dump -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
#python _ys4.py --mte_optimizer -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -t3 "$TABLE3"
#python _ys4.py --insert -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2"
