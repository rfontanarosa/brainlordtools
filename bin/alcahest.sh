#!/bin/bash

GAME_ID="alcahest"

source ./_common.sh

SOURCE="$RESOURCE_PATH/roms/Alcahest (J) [T+Eng1.0_FH+KM].smc"
DESTINATION="$RESOURCE_PATH/roms/Alcahest (I).sfc"

CURRENT_PATH=$PWD
cd "$BRAINLORD_PATH/alcahest-tool"
uv run alcahest-tool dump --rom "$SOURCE" --output "$RESOURCE_PATH/dump_all"
uv run alcahest-tool build --rom "$SOURCE" --translated "$RESOURCE_PATH/translated_all" --output "$DESTINATION" --tbl "$RESOURCE_PATH/tables/alcahest_ita.tbl"
cd $CURRENT_PATH
