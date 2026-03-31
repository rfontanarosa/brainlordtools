#!/bin/bash

GAME_ID=${1:-"som"}

source ./_common.sh

log_info "Starting import dump process"

case $GAME_ID in
  "alcahest")
    DUMP_DIR="$RESOURCE_PATH/dump_all"
    SOURCE_FILE_1="$DUMP_DIR/dialogue.txt"

    check_file "$SOURCE_FILE_1"

    log_step "Importing $SOURCE_FILE_1 [game=${YELLOW}$GAME_ID${NC}"
    python "$SCRIPT_DIR/manager.py" import_dump \
       -db "$DB" -s "$SOURCE_FILE_1"
    ;;

  "ffmq" | "gaia")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}"
    python "$SCRIPT_DIR/manager.py" import_dump \
       -db "$DB" -s "$SOURCE_FILE"
    ;;

  "soe")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}"
    python "$SCRIPT_DIR/manager.py" import_dump \
       -db "$DB" -s "$SOURCE_FILE" -g "$GAME_ID"
    ;;

  "som")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_EVENTS_FILE="$DUMP_DIR/dump_events_eng.txt"
    SOURCE_TEXT_FILE="$DUMP_DIR/dump_texts_eng.txt"

    check_file "$SOURCE_EVENTS_FILE"
    check_file "$SOURCE_TEXT_FILE"

    log_step "Importing $SOURCE_EVENTS_FILE [game=${YELLOW}$GAME_ID${NC}"
    python "$SCRIPT_DIR/manager.py" import_dump \
        -db "$DB" -s "$SOURCE_EVENTS_FILE"

    log_step "Importing $SOURCE_TEXT_FILE [game=${YELLOW}$GAME_ID${NC}"
    python "$SCRIPT_DIR/manager.py" import_dump \
        -db "$DB" -s "$SOURCE_TEXT_FILE"
    ;;

  "starocean")
    DUMP_DIR="$RESOURCE_PATH/chester/resources"
    SOURCE_FILE="$DUMP_DIR/dialogues.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}"
    python "$SCRIPT_DIR/manager.py" import_dump \
       -db "$DB" -s "$SOURCE_FILE" -g "$GAME_ID"
    ;;

  *)
    log_error "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac

log_success "All tasks completed successfully!"
log_info "Database location: ${YELLOW}$DB${NC}"
