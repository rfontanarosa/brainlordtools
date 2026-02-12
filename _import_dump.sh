#!/bin/bash

GAME_ID=${1:-"som"}

source ./_common.sh

log_info "Starting process for Game ID: ${YELLOW}$GAME_ID${NC}"

case $GAME_ID in
  "ffmq" | "gaia")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"
    log_step "Importing $SOURCE_FILE"
    python -m brainlordutils.utils import_dump \
       -db "$DB" -s "$SOURCE_FILE"
    ;;

  "soe")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"
    log_step "Importing $SOURCE_FILE"
    python -m brainlordutils.utils import_dump \
       -db "$DB" -s "$SOURCE_FILE" -g "$GAME_ID"
    ;;

  "som")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_EVENTS_FILE="$DUMP_DIR/dump_events_eng.txt"
    SOURCE_TEXT_FILE="$DUMP_DIR/dump_texts_eng.txt"

    check_file "$SOURCE_EVENTS_FILE"
    check_file "$SOURCE_TEXT_FILE"

    log_step "Importing $SOURCE_EVENTS_FILE"
    python -m brainlordutils.utils import_dump \
        -db "$DB" -s "$SOURCE_EVENTS_FILE"

    log_step "Importing $SOURCE_TEXT_FILE"
    python -m brainlordutils.utils import_dump \
        -db "$DB" -s "$SOURCE_TEXT_FILE"
    ;;

  "starocean")
    DUMP_DIR="$RESOURCE_PATH/chester/resources"
    SOURCE_FILE="$DUMP_DIR/dialogues.txt"

    check_file "$SOURCE_FILE"
    log_step "Importing dump(s) for $GAME_ID"
    python -m brainlordutils.utils import_dump \
       -db "$DB" -s "$SOURCE_FILE" -g "$GAME_ID"
    ;;

  *)
    log_error "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac

log_success "All tasks completed successfully!"
log_info "Database location: ${YELLOW}$DB${NC}"
