#!/bin/bash

GAME_ID="ys4"

source ./_common.sh

USER="clomax"
DUMP_PATH="$RESOURCE_PATH/dump"
DB="$RESOURCE_PATH/db/$GAME_ID.db"

SOURCE="$RESOURCE_PATH/roms/Ys IV - Mask of the Sun (U).sfc"
DESTINATION="$RESOURCE_PATH/roms/Ys IV - Mask of the Sun (I).sfc"

TABLE1="$RESOURCE_PATH/tables/Ys IV - Mask of the Sun (U).tbl"
TABLE2="$RESOURCE_PATH/tables/Ys IV - Mask of the Sun (I).tbl"
TABLE3="$RESOURCE_PATH/tables/Ys IV - Mask of the Sun.base.tbl"

MTE_OPTIMIZER_PATH="$RESOURCE_PATH/../.."
TEMP_PATH="$RESOURCE_PATH/../../temp"

python "$MANAGER_PATH/manager.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1

#python ../brainlordtools/ys4.py mte_finder -s "$SOURCE" -t1 "$TABLE1"
python ../brainlordtools/ys4.py dump -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_PATH" -db "$DB"
#python ../brainlordtools/ys4.py mte_optimizer -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -t3 "$TABLE3" -tp "$TEMP_PATH" -mop "$MTE_OPTIMIZER_PATH" -db "$DB" -u "$USER"
#python ../brainlordtools/ys4.py insert -d "$DESTINATION" -t2 "$TABLE2" -db "$DB" -u "$USER"
