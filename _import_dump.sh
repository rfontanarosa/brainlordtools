#!/bin/bash

GAME_ID=${1:-"som"}
USER=${2:-"clomax"}

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/$GAME_ID"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"

case $GAME_ID in
  "ffmq" | "gaia")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_eng.txt"

    echo "Processing $GAME_ID..."
    python -m brainlordutils.utils import_dump \
       -db "$DB" -s "$SOURCE_FILE"
    echo "Done!"
    ;;

  *)
    echo "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac
