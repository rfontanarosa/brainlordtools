#!/bin/bash

GAME_ID="equinox"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Equinox (U) [!].sfc"
DESTINATION="$RESOURCE_PATH/roms/Equinox (I) [!].sfc"

TABLE1="$RESOURCE_PATH/tables/Equinox (U) [!].tbl"

# DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

# TRANSLATED_TEXT_PATH="$RESOURCE_PATH/translated_text"
# TRANSLATED_GFX_PATH="$RESOURCE_PATH/translated_gfx"
TRANSLATED_MISC_PATH="$RESOURCE_PATH/translated_misc"

python "$MANAGER_PATH/manager.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1
python "$MANAGER_PATH/manager.py" copy_file -s "$SOURCE" -d "$DESTINATION" || exit 1
python "$MANAGER_PATH/manager.py" expand -d "$DESTINATION" -g "$GAME_ID" || exit 1

python "$TOOLS_PATH/equinox.py" dump_gfx -s "$SOURCE" -dp "$DUMP_GFX_PATH"
python "$TOOLS_PATH/equinox.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/equinox.py" insert_misc -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATED_MISC_PATH"

require_asar
asar "$RESOURCE_PATH/asm/gfx.asm" "$DESTINATION"
asar "$RESOURCE_PATH/asm/intro.asm" "$DESTINATION"
asar "$RESOURCE_PATH/asm/attract_mode.asm" "$DESTINATION"
asar "$RESOURCE_PATH/asm/windows.asm" "$DESTINATION"
