#!/bin/bash

RESOURCE_PATH="./resources/bof"

USER="clomax"
DB="$RESOURCE_PATH/db/bof.db"
SOURCE="$RESOURCE_PATH/gemini/roms/bof.smc"
DESTINATION="$RESOURCE_PATH/gemini/roms/bof-ita.smc"
MISC="$RESOURCE_PATH/misc.csv"
#DESTINATION="$RESOURCE_PATH/gemini/roms/bof-ita1.smc"
#MISC="$RESOURCE_PATH/misc1.csv"
TABLE1="$RESOURCE_PATH/tables/Breath of Fire (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Breath of Fire (I) [!].tbl"
TABLE3="$RESOURCE_PATH/tables/Breath of Fire (U) [!].base.tbl"
MTE_OPTIMIZER_PATH="$RESOURCE_PATH/../.."
TEMP_PATH="$RESOURCE_PATH/../../temp"

#python _bof.py mte_optimizer -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -t3 "$TABLE3" -tp "$TEMP_PATH" -mop "$MTE_OPTIMIZER_PATH" -db "$DB" -u "$USER"
#python _bof-gemini.py insert -d "$DESTINATION" -t2 "$TABLE2" -db "$DB" -u "$USER"
#python _bof.py insert_misc -d "$DESTINATION" -m1 "$MISC" -t3 "$TABLE3"
