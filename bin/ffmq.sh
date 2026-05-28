#!/bin/bash

GAME_ID="ffmq"

source ./_common.sh

USER="clomax"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"
SOURCE="$RESOURCE_PATH/roms/Final Fantasy - Mystic Quest (U) (V1.1).sfc"
DESTINATION="$BRAINLORD_PATH/Final-Fantasy-Mystic-Quest-ITA/ffmq_new.sfc"

TABLE1="$RESOURCE_PATH/tables/ffmq.tbl"

DUMP_MISC_PATH="$RESOURCE_PATH/dump_misc"

TRANSLATION_MISC_PATH="$RESOURCE_PATH/translation_misc"

python "$MANAGER_PATH/manager.py" crc_check -s "$SOURCE" -g "$GAME_ID" || exit 1

CURRENT_PATH=$PWD
cd "$BRAINLORD_PATH/Final-Fantasy-Mystic-Quest-ITA" || exit 1
cp "$SOURCE" .
python FFMQtool.py extract "Final Fantasy - Mystic Quest (U) (V1.1).sfc"
rm ffmq_new.sfc
cp "Final Fantasy - Mystic Quest (U) (V1.1).sfc" ffmq_new.sfc
require_asar
asar ./hack/expand_rom.asm ffmq_new.sfc
asar ./hack/hack.asm ffmq_new.sfc
asar ./hack/menu_ita.asm ffmq_new.sfc
asar ./hack/gfx_mapping_ita.asm ffmq_new.sfc
asar ./hack/store_messages.asm ffmq_new.sfc
asar ./hack/credits.asm ffmq_new.sfc
python FFMQtool.py insert ffmq_new.sfc dump_ita.txt font_ita.bin battle_ita.bin
cd "$CURRENT_PATH"

python "$TOOLS_PATH/ffmq.py" dump_misc -s "$SOURCE" -t1 "$TABLE1" -dp "$DUMP_MISC_PATH"

python "$TOOLS_PATH/ffmq.py" insert_misc -d "$DESTINATION" -t1 "$TABLE1" -tp "$TRANSLATION_MISC_PATH"

CURRENT_PATH=$PWD
cd "$BRAINLORD_PATH/Final-Fantasy-Mystic-Quest-ITA" || exit 1
require_asar
asar ./hack/various.asm ffmq_new.sfc
cp ffmq_new.sfc "$RESOURCE_PATH/roms/Final Fantasy - Mystic Quest (I) (V1.1).sfc"
cd "$CURRENT_PATH"
