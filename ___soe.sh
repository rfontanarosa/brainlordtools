#!/bin/bash

SOURCE="./resources/soe/roms/evermore_original.sfc"
DESTINATION="./resources/soe/roms/evermore.sfc"
TABLE1="./resources/soe/tables/soe.tbl"

python _soe.py --dump -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1"
python _soe.py --insert -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1"
