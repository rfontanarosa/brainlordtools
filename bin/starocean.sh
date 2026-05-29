#!/bin/bash

GAME_ID="starocean"

source ./_common.sh

SOURCE_EN="$RESOURCE_PATH/roms/Star_Ocean_U.sfc"
SOURCE_ES="$RESOURCE_PATH/roms/Star_Ocean_ES.sfc"
DESTINATION="$RESOURCE_PATH/roms/Star_Ocean_IT.sfc"

CURRENT_PATH=$PWD
cd $BRAINLORD_PATH/PrivateRomhacking
# uv run starocean extract $SOURCE_EN $SOURCE_ES
uv run starocean reinsert $SOURCE_ES
cd $CURRENT_PATH
