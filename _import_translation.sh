#!/bin/bash

GAME_ID=${1:-"som"}
USER=${2:-"clomax"}

source ./_common.sh

log_info "Starting process for Game ID: ${YELLOW}$GAME_ID${NC}"

case $GAME_ID in
  "brainlord")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/dump_text"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"
    check_file "$ORIGINAL_DUMP_PATH"

    log_step "Importing $SOURCE_FILE for user $USER"
    python "$SCRIPT_DIR/manager.py" import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH"
    ;;

  "brainlord_pt")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_por.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/dump_text"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"
    check_file "$ORIGINAL_DUMP_PATH"

    log_step "Importing $SOURCE_FILE for user $USER"
    python "$SCRIPT_DIR/manager.py" import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH"
    ;;

  "gaia")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/dump_text"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"
    check_file "$ORIGINAL_DUMP_PATH"

    log_step "Importing $SOURCE_FILE for user $USER"
    python "$SCRIPT_DIR/manager.py" import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH"
    ;;

  "ignition" | "spike")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE for user $USER"
    python "$SCRIPT_DIR/manager.py" import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER"
    ;;

  "som")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_EVENTS_FILE="$TRANSLATED_DUMP_DIR/dump_events_$USER.txt"
    SOURCE_TEXT_FILE="$TRANSLATED_DUMP_DIR/dump_texts_$USER.txt"

    check_file "$SOURCE_EVENTS_FILE"
    check_file "$SOURCE_TEXT_FILE"

    log_step "Importing $SOURCE_FILE for user $USER"
    python "$SCRIPT_DIR/manager.py" import_translation \
        -db "$DB" -s "$SOURCE_EVENTS_FILE" -u "$USER"
    log_step "Importing $SOURCE_FILE for user $USER"
    python "$SCRIPT_DIR/manager.py" import_translation \
        -db "$DB" -s "$SOURCE_TEXT_FILE" -u "$USER"
    ;;

  "starocean")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/chester/translated"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dialogues.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/chester/resources"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dialogues.txt"

    check_file "$SOURCE_FILE"
    check_file "$ORIGINAL_DUMP_PATH"

    log_step "Importing $SOURCE_FILE for user $USER"
    python "$SCRIPT_DIR/manager.py" import_translation \
        -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH" -g $GAME_ID
    ;;

  *)
    log_error "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac

log_success "All tasks completed successfully!"
log_info "Database location: ${YELLOW}$DB${NC}"
