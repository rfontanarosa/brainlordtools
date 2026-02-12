#!/bin/bash

GAME_ID=${1:-"som"}
SERVICE=${2:-"amazon"}

source ./_common.sh

log_info "Starting process for Game ID: ${YELLOW}$GAME_ID${NC}"

case $GAME_ID in
  "som")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_texts_eng.txt"
    DESTINATION_DIR="$RESOURCE_PATH/translation_text"

    check_file "$SOURCE_FILE"

    case $SERVICE in
      "amazon")
        DESTINATION_FILE="$DESTINATION_DIR/dump_texts_amazon_eng.txt"

        log_step "Translating $SOURCE_FILE using $SERVICE"
        python "$SCRIPT_DIR/manager.py" $SERVICE \
          -s "$SOURCE_FILE" -d "$DESTINATION_FILE" -g $GAME_ID
        ;;

      "deepl")
        DESTINATION_FILE="$DESTINATION_DIR/dump_texts_deepl_eng.txt"

        log_step "Translating $SOURCE_FILE using $SERVICE"
        python "$SCRIPT_DIR/manager.py" $SERVICE \
          -s "$SOURCE_FILE" -d "$DESTINATION_FILE"
        ;;

      *)
        log_error "Unknown SERVICE: $SERVICE"
        exit 1
        ;;
    esac

  *)
    log_error "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac

log_success "All tasks completed successfully!"
