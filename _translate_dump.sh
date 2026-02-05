#!/bin/bash

GAME_ID=${1:-"som"}
SERVICE=${2:-"amazon"}

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/$GAME_ID"

case $GAME_ID in
  "som")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_texts_eng.txt"
    DESTINATION_DIR="$RESOURCE_PATH/translation_text"

    case $SERVICE in
      "amazon")
        DESTINATION_FILE="$DESTINATION_DIR/dump_texts_amazon_eng.txt"

        echo "Processing $GAME_ID using $SERVICE..."
        python -m brainlordutils.translators $SERVICE \
          -s "$SOURCE_FILE" -d "$DESTINATION_FILE" -g $GAME_ID
        echo "Done!"
        ;;

      "deepl")
        DESTINATION_FILE="$DESTINATION_DIR/dump_texts_deepl_eng.txt"

        echo "Processing $GAME_ID using $SERVICE..."
        python -m brainlordutils.translators $SERVICE \
          -s "$SOURCE_FILE" -d "$DESTINATION_FILE"
        echo "Done!"
        ;;

      *)
        echo "Unknown SERVICE: $SERVICE"
        exit 1
        ;;
    esac

  *)
    echo "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac
