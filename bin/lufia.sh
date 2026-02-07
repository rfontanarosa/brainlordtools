#!/bin/bash

GAME_ID="lufia"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Lufia & The Fortress of Doom (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Lufia & The Fortress of Doom (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/AllOriginal.tbl"
TABLE2="$RESOURCE_PATH/tables/LufiaScriptIta.tbl"
TABLE3="$RESOURCE_PATH/tables/LufiaMenuIta.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

python "$TOOLS_PATH/_utils.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1
python "$TOOLS_PATH/_utils.py" copy_file -s "$SOURCE" -d "$DESTINATION" || exit 1
python "$TOOLS_PATH/_utils.py" expand -d "$DESTINATION" -g "$GAME_ID" || exit 1

python "$TOOLS_PATH/lufia.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/lufia.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"
python "$TOOLS_PATH/lufia.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"

python "$TOOLS_PATH/lufia.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t2 "$TABLE2" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
python "$TOOLS_PATH/lufia.py" insert_misc -d "$DESTINATION" -t1 "$TABLE1" -t2 "$TABLE3" -tp "$TRANSLATION_MISC_PATH"
python "$TOOLS_PATH/lufia.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"

if ! command -v asar &> /dev/null
then
  echo "Command 'asar' not found."
  exit
else
  asar "$RESOURCE_PATH/asm/hack.asm" "$DESTINATION"
  asar "$RESOURCE_PATH/asm/various.asm" "$DESTINATION"
  asar "$RESOURCE_PATH/asm/menus.asm" "$DESTINATION"
  asar "$RESOURCE_PATH/asm/battle_msg.asm" "$DESTINATION"
  asar "$RESOURCE_PATH/asm/levelup_msg.asm" "$DESTINATION"
  asar "$RESOURCE_PATH/asm/end_stats.asm" "$DESTINATION"
fi
