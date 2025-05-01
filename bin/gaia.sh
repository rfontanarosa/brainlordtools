#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/gaia"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="clomax"
DB="$RESOURCE_PATH/db/gaia.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Illusion of Gaia (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Illusion of Gaia (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/Illusion of Gaia (U) [!].tbl"
TABLE2="$RESOURCE_PATH/tables/Illusion of Gaia (I) [!].tbl"
TABLE3="$RESOURCE_PATH/tables/illusion_of_gaia-menu.tbl"
TABLE4="$RESOURCE_PATH/tables/illusion_of_gaia-intro.tbl"
TABLE5="$RESOURCE_PATH/tables/illusion_of_gaia-intro_it.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

python "$TOOLS_PATH/_utils.py" file_copy -s "$SOURCE" -d "$DESTINATION"
python "$TOOLS_PATH/gaia.py" expand -d "$DESTINATION"

python "$TOOLS_PATH/gaia.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -t3 "$TABLE4" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/gaia.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -t2 "$TABLE3" -t3 "$TABLE4" -dp "$DUMP_MISC_PATH"
python "$TOOLS_PATH/gaia.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"

python "$TOOLS_PATH/gaia.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -t3 "$TABLE5" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
python "$TOOLS_PATH/gaia.py" insert_misc -d "$DESTINATION" -t1 "$TABLE2" -t2 "$TABLE3" -t3 "$TABLE5" -tp "$TRANSLATION_MISC_PATH"
python "$TOOLS_PATH/gaia.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"

if ! command -v asar &> /dev/null
then
  echo "Command 'asar' not found."
  exit
else
  asar "$RESOURCE_PATH/asm/main.asm" "$DESTINATION"
fi
