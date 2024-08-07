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
TABLE5="$RESOURCE_PATH/tables/gargoyle_eng_initial_screen.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

python "$TOOLS_PATH/_utils.py" file_copy -s "$SOURCE" -d "$DESTINATION"

python "$TOOLS_PATH/gargoyle.py" --no_crc32_check dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH"
python "$TOOLS_PATH/gargoyle.py" --no_crc32_check dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python "$TOOLS_PATH/gargoyle.py" --no_crc32_check dump_misc -s "$SOURCE" -t1 "$TABLE1" -t2 "$TABLE2" -t3 "$TABLE5" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/gargoyle.py" --no_crc32_check insert_text -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE4" -t2 "$TABLE3" -tp1 "$TRANSLATION_TEXT_PATH" -tp2 "$TRANSLATION_MISC_PATH"
python "$TOOLS_PATH/gargoyle.py" --no_crc32_check insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
python "$TOOLS_PATH/gargoyle.py" --no_crc32_check insert_misc -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE2" -t3 "$TABLE5" -tp "$TRANSLATION_MISC_PATH"

if ! command -v bass &> /dev/null
then
  echo "Command 'bass' not found."
  exit
else
  # bass "$RESOURCE_PATH/asm/accents_hack.asm" -m "$DESTINATION"
  bass "$RESOURCE_PATH/asm/various.asm" -m "$DESTINATION"
fi

# python ../mteOpt.py table -s /Users/robertofontanarosa/git/brainlordresources/gargoyle/translation_text/dump_ita.txt -d dict.txt -c clean.txt -b 1 -M 10 -l 112 -o 128 --game gargoyle
