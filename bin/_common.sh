#!/bin/bash

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/$GAME_ID"
MANAGER_PATH="$BRAINLORD_PATH/brainlordtools"
TOOLS_PATH="$BRAINLORD_PATH/brainlordtools/brainlordtools"

require_asar() {
  if ! command -v asar &> /dev/null; then
    echo "Command 'asar' not found."
    exit 1
  fi
}
