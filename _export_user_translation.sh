#!/bin/bash

GAME_ID=${1:-"som"}
USER=${2:-"clomax"}

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/$GAME_ID"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"

case $GAME_ID in
  "ignition" | "spike")
    DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$DUMP_DIR/dump_ita_$USER.txt"

    mkdir -p "$DUMP_DIR"
    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.export_user_translation export_user_translation \
        -u "$USER" -db "$DB" -d "$DEST_FILE"
    echo "Done! Files saved in $DUMP_DIR"
    ;;

  "som")
    DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_EVENTS_FILE="$DUMP_DIR/dump_events_$USER.txt"
    DEST_TEXT_FILE="$DUMP_DIR/dump_texts_$USER.txt"

    mkdir -p "$DUMP_DIR"
    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.export_user_translation export_user_translation \
        -u "$USER" -db "$DB" -d "$DEST_EVENTS_FILE" -b 1 2
    python -m brainlordutils.export_user_translation export_user_translation \
        -u "$USER" -db "$DB" -d "$DEST_TEXT_FILE" -b 3 4 5 6 7 8
    echo "Done! Files saved in $DUMP_DIR"
    ;;

  *)
    echo "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac
