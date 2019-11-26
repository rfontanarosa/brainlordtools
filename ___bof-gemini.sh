#!/bin/bash

USER="clomax"
DB="./resources/bof/db/bof.db"
SOURCE="./resources/bof/gemini/roms/bof.smc"
DESTINATION="./resources/bof/gemini/roms/bof-ita.smc"
MISC="./resources/bof/misc.csv"
#DESTINATION="./resources/bof/gemini/roms/bof-ita1.smc"
#MISC="./resources/bof/misc1.csv"
TABLE1="./resources/bof/tables/Breath of Fire (U) [!].tbl"
TABLE2="./resources/bof/tables/Breath of Fire (I) [!].tbl"
TABLE3="./resources/bof/tables/Breath of Fire (U) [!].base.tbl"

#python _bof.py --mte_optimizer -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -t3 "$TABLE3"
#python _bof-gemini.py --insert -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -t3 "$TABLE3"
#python _bof.py --insert_misc -u "$USER" -db "$DB" -s "$SOURCE" -d "$DESTINATION" -m "$MISC" -t1 "$TABLE1" -t2 "$TABLE2" -t3 "$TABLE3"
