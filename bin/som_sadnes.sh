#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/som"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

USER="sadnes"
DB="$RESOURCE_PATH/db/som.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Secret of Mana (ITA - SADNESS).sfc"

TABLE1="$RESOURCE_PATH/tables/som_main.tbl"
TABLE2="$RESOURCE_PATH/tables/som_main_with_dte.tbl"
TABLE3="$RESOURCE_PATH/tables/som_main_with_dte_sadnes.tbl"
TABLE4="$RESOURCE_PATH/tables/som_main_with_dte_ita.tbl"
TABLE5="$RESOURCE_PATH/tables/som_main_ita.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/sadnes/dump_text"
DUMP_GFX_PATH="$RESOURCE_PATH/sadnes/dump_gfx"
DUMP_MISC_PATH="$RESOURCE_PATH/sadnes/dump_misc"

python "$TOOLS_PATH/som.py" --no_crc32_check dump_text -s "$SOURCE" -t1 "$TABLE3" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/som.py" --no_crc32_check dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/somtools/decomp.py" "$SOURCE" "$DUMP_MISC_PATH/intro.bin" --base-offset="7B480"
python "$TOOLS_PATH/somtools/decomp.py" "$SOURCE" "$DUMP_MISC_PATH/title.bin" --base-offset="1CE800"
python "$TOOLS_PATH/somtools/decomp.py" "$SOURCE" "$DUMP_MISC_PATH/font-intro.bin" --base-offset="7C1C0"
python "$TOOLS_PATH/somtools/decomp.py" "$SOURCE" "$DUMP_MISC_PATH/intro-code.bin" --base-offset="77C00"

python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_equip.bin" --sprite 9
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_hp_down.bin" --sprite 16
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_hp_up.bin" --sprite 17
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_mp_down.bin" --sprite 62
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_mp_up.bin" --sprite 63
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_stat.bin" --sprite 170
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_level.bin" --sprite 171
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_act.bin" --sprite 172
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_controller_edit.bin" --sprite 173
python "$TOOLS_PATH/somtools/som_icons.py" extract "$SOURCE" "$DUMP_GFX_PATH/menu_icon_win_edit.bin" --sprite 174
