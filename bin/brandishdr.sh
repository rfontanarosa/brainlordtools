#!/bin/bash

GAME_ID="brandishdr"

source ./_common.sh

CURRENT_PATH=$PWD
cd "$BRAINLORD_PATH/brandish-dr-tool"
uv run brandish build --translated-dir "$RESOURCE_PATH/translated"
cd $CURRENT_PATH
