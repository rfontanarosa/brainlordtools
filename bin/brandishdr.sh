#!/bin/bash

source ./_common.sh

CURRENT_PATH=$PWD
cd "$BRAINLORD_PATH/brandish-dr-tool"
uv run brandish build --translated-dir "$RESOURCE_PATH/brandishdr/translated"
cd $CURRENT_PATH
