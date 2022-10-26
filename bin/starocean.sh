#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/starocean"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

SOURCE="$RESOURCE_PATH/roms/Star_Ocean_ES.sfc"
DESTINATION="$RESOURCE_PATH/roms/patched_Star_Ocean_ES.sfc"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

CURRENT_PATH=$PWD
cd /Users/robertofontanarosa/git/Romhacking
source ./venv/bin/activate
# python -m starocean.main extract $RESOURCE_PATH/roms/Star_Ocean_U.sfc $DUMP_TEXT_PATH/dump_eng.txt
python -m starocean.main reinsert $SOURCE $TRANSLATION_TEXT_PATH/dump_eng.txt
deactivate
cd $CURRENT_PATH

python "$TOOLS_PATH/starocean.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"

python "$TOOLS_PATH/starocean.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
