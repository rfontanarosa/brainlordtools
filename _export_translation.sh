#!/bin/bash

GAME_ID=${1:-"som"}
USER=${2:-"clomax"}

source ./_common.sh

log_info "Starting process for Game ID: ${YELLOW}$GAME_ID${NC}"

case $GAME_ID in
  "brainlord")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    log_step "Exporting $GAME_ID translation to $DEST_FILE"
    mkdir -p "$TRANSLATED_DUMP_DIR"
    python "$SCRIPT_DIR/manager.py" export_translation \
       -db "$DB" -d "$DEST_FILE" -b 1 2 3 4 5 6 7
    python "$SCRIPT_DIR/manager.py" export_translation \
       -db "$DB" -d "$DEST_USER_FILE" -u "$USER" -b 1 2 3 4 5 6 7
    ;;

  "7thsaga" | "gaia" | "ignition" | "spike")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    log_step "Exporting $GAME_ID translation to $DEST_FILE"
    mkdir -p "$TRANSLATED_DUMP_DIR"
    python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_FILE"
    python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_USER_FILE" -u "$USER"
    ;;

  "ffmq" | "lufia")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    log_step "Exporting $GAME_ID translation to $DEST_FILE"
    mkdir -p "$TRANSLATED_DUMP_DIR"
    python "$SCRIPT_DIR/manager.py" export_translation \
       -db "$DB" -d "$DEST_FILE" -b 1
    python "$SCRIPT_DIR/manager.py" export_translation \
       -db "$DB" -d "$DEST_USER_FILE" -u "$USER" -b 1
    ;;

  "som")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_USER_EVENTS_FILE="$TRANSLATED_DUMP_DIR/dump_events_$USER.txt"
    DEST_USER_TEXT_FILE="$TRANSLATED_DUMP_DIR/dump_texts_$USER.txt"

    log_step "Exporting $GAME_ID translation to $DEST_FILE"
    mkdir -p "$TRANSLATED_DUMP_DIR"
    python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_USER_EVENTS_FILE" -u "$USER" -b 1 2
    python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_USER_TEXT_FILE" -u "$USER" -b 3 4 5 6 7 8
    ;;

  *)
    echo "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac

log_success "All tasks completed successfully!"
log_info "Database location: ${YELLOW}$TRANSLATED_DUMP_DIR${NC}"
