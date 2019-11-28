#!/bin/bash

RESOURCE_PATH="./resources/soe"

SOURCE="$RESOURCE_PATH/roms/evermore.sfc"
DESTINATION="$RESOURCE_PATH/roms/patched_evermore.sfc"
TABLE1="$RESOURCE_PATH/tables/soe.tbl"

python _soe.py --dump -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1"
python _soe.py --insert -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1"
