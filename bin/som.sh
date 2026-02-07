#!/bin/bash

GAME_ID="som"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Secret of Mana (USA).sfc"
DESTINATION="$RESOURCE_PATH/roms/Secret of Mana (ITA).sfc"

TABLE1="$RESOURCE_PATH/tables/som_main.tbl"
TABLE2="$RESOURCE_PATH/tables/som_main_with_dte.tbl"
TABLE3="$RESOURCE_PATH/tables/som_main_with_dte_sadnes.tbl"
TABLE4="$RESOURCE_PATH/tables/som_main_with_dte_ita.tbl"
TABLE5="$RESOURCE_PATH/tables/som_main_ita.tbl"
TABLE6="$RESOURCE_PATH/tables/som_credits.tbl"

DUMP_TEXT_PATH="$RESOURCE_PATH/dump_text"
DUMP_GFX_PATH="$RESOURCE_PATH/dump_gfx"
DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TRANSLATION_TEXT_PATH="$RESOURCE_PATH/translation_text"
TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"
TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"
TRANSLATION_CUSTOM_PATH="$RESOURCE_PATH/translation_custom"

python "$TOOLS_PATH/_utils.py" copy_file -s "$SOURCE" -d "$DESTINATION"

python "$TOOLS_PATH/som.py" dump_text -s "$SOURCE" -t1 "$TABLE1" -t2 "$TABLE6" -dp "$DUMP_TEXT_PATH" -db "$DB"
python "$TOOLS_PATH/som.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/somtools/decomp.py" "$SOURCE" "$DUMP_MISC_PATH/intro-code.bin" --base-offset="77C00"
python "$TOOLS_PATH/somtools/decomp.py" "$SOURCE" "$DUMP_MISC_PATH/intro-data.bin" --base-offset="7B480"
python "$TOOLS_PATH/somtools/decomp.py" "$SOURCE" "$DUMP_MISC_PATH/title.bin" --base-offset="1CE800"

python "$TOOLS_PATH/som.py" dump_tilemap -s "$DUMP_MISC_PATH/intro-data.bin" -dp "$DUMP_MISC_PATH"

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

if ! command -v asar &> /dev/null
then
  echo "Command 'asar' not found."
  exit
else
  asar "$RESOURCE_PATH/asm/intro_ram.asm" "$TRANSLATION_MISC_PATH/intro-code.bin"
fi

python "$TOOLS_PATH/som.py" insert_tilemap -d "$TRANSLATION_MISC_PATH/intro-data.bin" -tp "$TRANSLATION_MISC_PATH"

python "$TOOLS_PATH/somtools/decomp.py" "$TRANSLATION_MISC_PATH/intro-code.bin" "$TRANSLATION_MISC_PATH/intro-code-compressed.bin" --compress --compression-key="1"
python "$TOOLS_PATH/somtools/decomp.py" "$TRANSLATION_MISC_PATH/intro-data.bin" "$TRANSLATION_MISC_PATH/intro-data-compressed.bin" --compress --compression-key="4"
python "$TOOLS_PATH/somtools/decomp.py" "$TRANSLATION_MISC_PATH/title.bin" "$TRANSLATION_MISC_PATH/title-compressed.bin" --compress --compression-key="3"

python "$TOOLS_PATH/som.py" insert_text -s "$SOURCE" -d "$DESTINATION" -t1 "$TABLE4" -t2 "$TABLE6" -tp "$TRANSLATION_TEXT_PATH" -db "$DB" -u "$USER"
python "$TOOLS_PATH/som.py" insert_misc -d "$DESTINATION" -t1 "$TABLE5" -tp "$TRANSLATION_MISC_PATH"

python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_equip.bin" "$DESTINATION" --sprite 9
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_hp_down.bin" "$DESTINATION" --sprite 16
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_hp_up.bin" "$DESTINATION" --sprite 17
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_mp_down.bin" "$DESTINATION" --sprite 62
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_mp_up.bin" "$DESTINATION" --sprite 63
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_stat.bin" "$DESTINATION" --sprite 170
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_level.bin" "$DESTINATION" --sprite 171
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_act.bin" "$DESTINATION" --sprite 172
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_controller_edit.bin" "$DESTINATION" --sprite 173
python "$TOOLS_PATH/somtools/som_icons.py" insert "$TANSLATION_GFX_PATH/menu_icon_win_edit.bin" "$DESTINATION" --sprite 174

if ! command -v asar &> /dev/null
then
  echo "Command 'asar' not found."
  exit
else
  asar "$RESOURCE_PATH/asm/font.asm" "$DESTINATION"
  asar "$RESOURCE_PATH/asm/menus.asm" "$DESTINATION"
  asar "$RESOURCE_PATH/asm/intro.asm" "$DESTINATION"
fi

# python ../mteOpt.py table -s "$RESOURCE_PATH/translation_text/dump_ita.txt" -d "dict.txt" -c "clean.txt" -b 1 -m 2 -M 2 -l 59 -o 128 --game som

