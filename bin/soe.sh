#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/soe"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

SOURCE="$RESOURCE_PATH/roms/evermore.sfc"
DESTINATION="$RESOURCE_PATH/roms/patched_evermore.sfc"

TABLE1="$RESOURCE_PATH/tables/soe.tbl"

DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TRANSLATION_CUSTOM_PATH="$RESOURCE_PATH/translation_custom"

CURRENT_PATH=$PWD
cd $BRAINLORD_PATH/Romhacking
source ./venv/bin/activate
./bin/evertool reinsert $SOURCE $TRANSLATION_TEXT_PATH/dump_ita_clomax.txt
deactivate
cd $CURRENT_PATH

python "$TOOLS_PATH/soe.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python "$TOOLS_PATH/soe.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/soe.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
python "$TOOLS_PATH/soe.py" insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATION_MISC_PATH"
python "$TOOLS_PATH/soe.py" insert_custom -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATION_CUSTOM_PATH"

asar "$RESOURCE_PATH/asm/gfx_hack.asm" "$DESTINATION"
asar "$RESOURCE_PATH/asm/menu_text_ita.asm" "$DESTINATION"
