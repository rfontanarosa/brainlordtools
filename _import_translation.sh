#!/bin/bash

GAME_ID=${1:-"som"}
USER=${2:-"clomax"}

source ./_common.sh

case $GAME_ID in
  "brainlord")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/dump_text"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dump_eng.txt"

    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH"
    echo "Done! Dump has been imported into $DB"
    ;;

  "gaia")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/dump_text"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dump_eng.txt"

    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH"
    echo "Done! Dump has been imported into $DB"
    ;;

  "ignition" | "spike")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER"
    echo "Done! Dump has been imported into $DB"
    ;;

  "som")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_EVENTS_FILE="$TRANSLATED_DUMP_DIR/dump_events_$USER.txt"
    SOURCE_TEXT_FILE="$TRANSLATED_DUMP_DIR/dump_texts_$USER.txt"

    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils import_translation \
        -db "$DB" -s "$SOURCE_EVENTS_FILE" -u "$USER"
    python -m brainlordutils.utils import_translation \
        -db "$DB" -s "$SOURCE_TEXT_FILE" -u "$USER"
    echo "Done! Dumps have been imported into $DB"
    ;;

  "starocean")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/chester/translated"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dialogues.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/chester/resources"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dialogues.txt"

    echo "Processing $GAME_ID for user $USER..."
    python -m brainlordutils.utils import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH" -g $GAME_ID
    echo "Done! Dump has been imported into $DB"
    ;;

  *)
    echo "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac
