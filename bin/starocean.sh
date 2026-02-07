#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/starocean"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

SOURCE_EN="$RESOURCE_PATH/roms/Star_Ocean_U.sfc"
SOURCE_ES="$RESOURCE_PATH/roms/Star_Ocean_ES.sfc"
DESTINATION="$RESOURCE_PATH/roms/Star_Ocean_IT.sfc"

TABLE1="$RESOURCE_PATH/tables/star_ocean_ES_small.tbl"
TABLE2="$RESOURCE_PATH/tables/star_ocean_ES_small.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

python "$TOOLS_PATH/_utils.py" copy_file -s "$SOURCE_ES" -d "$DESTINATION"

python "$TOOLS_PATH/starocean.py" dump_misc -s "$SOURCE_ES" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"
python "$TOOLS_PATH/starocean.py" dump_gfx -s "$SOURCE_ES" -dp "$DUMP_GFX_PATH"

python "$TOOLS_PATH/starocean.py" insert_misc -d "$DESTINATION" -t1 "$TABLE2" -t2 "$TABLE2" -tp "$TRANSLATION_MISC_PATH"
python "$TOOLS_PATH/starocean.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
