BRAINLORD_PATH="/Users/robertofontanarosa/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/starocean"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

DESTINATION="$RESOURCE_PATH/roms/patched_Star_Ocean_ES.sfc"

TANSLATION_GFX_PATH="$RESOURCE_PATH/translation_gfx"

CURRENT_PATH=$PWD
cd /Users/robertofontanarosa/git/Romhacking
source ./venv/bin/activate
python -m starocean.main extract $RESOURCE_PATH/roms/Star_Ocean_U.sfc $RESOURCE_PATH/dump_text/dump_en.txt
#python -m starocean.main reinsert $RESOURCE_PATH/roms/Star_Ocean_ES.sfc $RESOURCE_PATH/dump_text/dump_en.txt
deactivate
cd $CURRENT_PATH

python "$TOOLS_PATH/starocean.py" insert_gfx -d "$DESTINATION" -tp "$TANSLATION_GFX_PATH"
