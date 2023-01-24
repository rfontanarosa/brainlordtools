#!/bin/bash

RESOURCE_PATH="../../brainlordresources/brainlord"

USER="clomax"
DB="$RESOURCE_PATH/db/brainlord.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Brain Lord (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Brain Lord (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/Brain Lord (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Brain Lord (I) [!].tbl"
TABLE3="$RESOURCE_PATH/tables/bl.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"
DUMP_CREDITS_PATH="$RESOURCE_PATH/dump_credits"

TANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"
TANSLATION_CREDITS_PATH="$RESOURCE_PATH/translation_credits"

python3 ../brainlordtools/brainlord.py expand -s "$SOURCE" -d "$DESTINATION"

python3 ../brainlordtools/brainlord.py dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
# python3 ../brainlordtools/brainlord.py dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
# python3 ../brainlordtools/brainlord.py dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"
# python3 ../brainlordtools/brainlord.py dump_credits -s "$SOURCE" -t3 "$TABLE3" -dp "$DUMP_CREDITS_PATH"

python3 ../brainlordtools/brainlord.py insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
python3 ../brainlordtools/brainlord.py insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
python3 ../brainlordtools/brainlord.py insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -tp "$TRANSLATION_MISC_PATH"
python3 ../brainlordtools/brainlord.py insert_credits -d "$DESTINATION" -t3 "$TABLE3" -tp "$TANSLATION_CREDITS_PATH"

asar "$RESOURCE_PATH/asm/main.asm" "$DESTINATION"

# SOURCE="$RESOURCE_PATH/roms/Brain Lord (I) [!] - 0x74000.sfc"
# DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx_mog"
# DESTINATION="$RESOURCE_PATH/roms/Brain Lord (U) [!] - 0x74000.sfc"
# TANSLATION_GFX_PATH="$RESOURCE_PATH/dump_gfx_mog"
# python3 ../brainlordtools/brainlord.py dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
# python3 ../brainlordtools/brainlord.py insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
