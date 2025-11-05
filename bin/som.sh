#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/som"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/som.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Secret of Mana (USA).sfc"
SOURCE="$RESOURCE_PATH/roms/Secret of Mana (ITA - SADNESS).sfc"
DESTINATION="$RESOURCE_PATH/roms/Secret of Mana (ITA).sfc"

TABLE1="$RESOURCE_PATH/tables/som_main.tbl"
TABLE2="$RESOURCE_PATH/tables/som_main_with_dte.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TRANSLATION_CUSTOM_PATH="$RESOURCE_PATH/translation_custom"

python "$TOOLS_PATH/_utils.py" file_copy -s "$SOURCE" -d "$DESTINATION"

python "$TOOLS_PATH/som.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"

python "$TOOLS_PATH/som.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"

