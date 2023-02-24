#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/gargoyle"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
SOURCE="$RESOURCE_PATH/roms/Gargoyle's Quest (USA, Europe).gb"
DESTINATION="$RESOURCE_PATH/roms/Gargoyle's Quest (ITA).gb"

TABLE1="$RESOURCE_PATH/tables/gargoyle_eng_dte.tbl"
TABLE2="$RESOURCE_PATH/tables/gargoyle_eng_menu.tbl"
TABLE3="$RESOURCE_PATH/tables/gargoyle_eng_without_dte.tbl"
TABLE4="$RESOURCE_PATH/tables/gargoyle_ita_dte.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

python "$TOOLS_PATH/_utils.py" file_copy -s "$SOURCE" -d "$DESTINATION"

python "$TOOLS_PATH/gargoyle.py" --no_crc32_check dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH"
python "$TOOLS_PATH/gargoyle.py" --no_crc32_check dump_misc -s "$SOURCE" -t1 "$TABLE1" -t2 "$TABLE2" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/gargoyle.py" --no_crc32_check insert_text -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE4" -t2 "$TABLE3" -tp1 "$TRANSLATION_TEXT_PATH"  -tp2 "$TRANSLATION_MISC_PATH"

