#!/bin/bash

GAME_ID=${1:-"som"}
USER1=${2:-"clomax"}
USER2=${3:-"xxx"}

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/$GAME_ID"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"

case $GAME_ID in
  "ignition" | "spike")
    DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$DUMP_DIR/dump_ita_$USER1.txt"

    echo "Processing $GAME_ID for user $USER1..."
    python -m brainlordutils.utils import_user_translation \
        -u "$USER2" -db "$DB" -s "$SOURCE_FILE"
    echo "Done! Files have been imported into $DB"
    ;;

  "som")
    DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_EVENTS_FILE="$DUMP_DIR/dump_events_$USER1.txt"
    SOURCE_TEXT_FILE="$DUMP_DIR/dump_texts_$USER1.txt"

    echo "Processing $GAME_ID for user $USER1..."
    python -m brainlordutils.utils import_user_translation \
        -u "$USER2" -db "$DB" -s "$SOURCE_EVENTS_FILE"
    python -m brainlordutils.utils import_user_translation \
        -u "$USER2" -db "$DB" -s "$SOURCE_TEXT_FILE"
    echo "Done! Files have been imported into $DB"
    ;;

  *)
    echo "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac
