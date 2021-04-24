#!/bin/bash

RESOURCE_PATH="../../brainlordresources/neugier"

USER="clomax"
DB="$RESOURCE_PATH/db/neugier.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Neugier (J) [T+Eng2.00_Haeleth&RPGOne].sfc"
DESTINATION="$RESOURCE_PATH/roms/Neugier - Umi to Kaze no Kodou (I).sfc"

TABLE1="$RESOURCE_PATH/tables/Neugier - Umi to Kaze no Kodou (U).tbl"
TABLE2="$RESOURCE_PATH/tables/Neugier - Umi to Kaze no Kodou (I).tbl"
TABLE3="$RESOURCE_PATH/tables/ascii.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"
DUMP_CREDITS_PATH="$RESOURCE_PATH/dump_credits"

TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

python3 ../brainlordtools/neugier.py dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
python3 ../brainlordtools/neugier.py dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python3 ../brainlordtools/neugier.py dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"
python3 ../brainlordtools/neugier.py dump_credits -s "$SOURCE" -t3 "$TABLE3" -dp "$DUMP_CREDITS_PATH"

python3 ../brainlordtools/neugier.py insert_text -d "$DESTINATION" -t2 "$TABLE2" -db "$DB" -u "$USER"
python3 ../brainlordtools/neugier.py insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
python3 ../brainlordtools/neugier.py insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE1" -tp "$TRANSLATION_MISC_PATH"
