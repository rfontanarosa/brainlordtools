#!/bin/bash

RESOURCE_PATH="../../brainlordresources/soe"

SOURCE="$RESOURCE_PATH/roms/evermore.sfc"
DESTINATION="$RESOURCE_PATH/roms/patched_evermore.sfc"

TABLE1="$RESOURCE_PATH/tables/soe.tbl"

DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

MISC1="$RESOURCE_PATH/misc.csv"

# cd /Users/rfontanarosa/git/Romhacking
# source ./venv/bin/activate
# ./bin/evertool reinsert /Users/rfontanarosa/git/brainlordresources/soe/roms/evermore.sfc /Users/rfontanarosa/git/brainlordresources/soe/dump_text/dump_ita.txt
# deactivate

python3 ../brainlordtools/soe.py dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python3 ../brainlordtools/soe.py dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python3 ../brainlordtools/soe.py insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
python3 ../brainlordtools/soe.py insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATION_MISC_PATH" -m1 "$MISC1"

asar "$RESOURCE_PATH/hack/menu_text_ita.asm" "$DESTINATION"
