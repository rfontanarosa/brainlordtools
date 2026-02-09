#!/bin/bash

GAME_ID=${1:-"som"}
USER=${2:-"clomax"}

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/$GAME_ID"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"

case $GAME_ID in
  "brainlord")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    mkdir -p "$TRANSLATED_DUMP_DIR"
    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils export_translation \
       -db "$DB" -d "$DEST_FILE" -b 1 2 3 4 5 6 7
    python -m brainlordutils.utils export_translation \
       -db "$DB" -d "$DEST_USER_FILE" -u "$USER" -b 1 2 3 4 5 6 7
    echo "Done! Translations have been saved in $TRANSLATED_DUMP_DIR"
    ;;

  "gaia" | "ignition" | "spike")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    mkdir -p "$TRANSLATED_DUMP_DIR"
    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils export_translation \
        -db "$DB" -d "$DEST_FILE"
    python -m brainlordutils.utils export_translation \
        -db "$DB" -d "$DEST_USER_FILE" -u "$USER"
    echo "Done! Translations have been saved in $TRANSLATED_DUMP_DIR"
    ;;

  "ffmq" | "lufia")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    mkdir -p "$TRANSLATED_DUMP_DIR"
    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils export_translation \
       -db "$DB" -d "$DEST_FILE" -b 1
    python -m brainlordutils.utils export_translation \
       -db "$DB" -d "$DEST_USER_FILE" -u "$USER" -b 1
    echo "Done! Translations have been saved in $TRANSLATED_DUMP_DIR"
    ;;

  "som")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_USER_EVENTS_FILE="$TRANSLATED_DUMP_DIR/dump_events_$USER.txt"
    DEST_USER_TEXT_FILE="$TRANSLATED_DUMP_DIR/dump_texts_$USER.txt"

    mkdir -p "$TRANSLATED_DUMP_DIR"
    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils export_translation \
        -db "$DB" -d "$DEST_USER_EVENTS_FILE" -u "$USER" -b 1 2
    python -m brainlordutils.utils export_translation \
        -db "$DB" -d "$DEST_USER_TEXT_FILE" -u "$USER" -b 3 4 5 6 7 8
    echo "Done! Translations have been saved in $TRANSLATED_DUMP_DIR"
    ;;

  *)
    echo "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac
