#!/bin/bash

set -euo pipefail

GAME_ID=${1:-""}

if [ -z "$GAME_ID" ]; then
  echo "Usage: $0 <game_id>" >&2
  exit 1
fi

source ./_common.sh

log_info "Starting import dump process for Game ID: ${YELLOW}$GAME_ID${NC}"

case "$GAME_ID" in
  "alcahest")
    DUMP_DIR="$RESOURCE_PATH/dump_all/text"

    SOURCE_FILES=(
      dialogue.txt
      ending.txt
      credits.txt
      items.txt
      inventory.txt
      partners.txt
      passwords_1.txt
      passwords_2.txt
      passwords_3.txt
      epilogue.txt
      events_1.txt
      events_2.txt
      events_misc.txt
      events_doors.txt
    )
    SOURCE_FILES=("${SOURCE_FILES[@]/#/$DUMP_DIR/}")

    for f in "${SOURCE_FILES[@]}"; do
      check_file "$f"
    done

    log_step "Importing ${SOURCE_FILES[0]} [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" \
      -s "${SOURCE_FILES[@]}"
    ;;

  "7thsaga" | "neugier" | "gaia")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" -s "$SOURCE_FILE"
    ;;

  "ffmq" | "soe")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE="$DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" -s "$SOURCE_FILE" -g "$GAME_ID"
    ;;

  "som")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_EVENTS_FILE="$DUMP_DIR/dump_events_eng.txt"
    SOURCE_TEXT_FILE="$DUMP_DIR/dump_texts_eng.txt"

    check_file "$SOURCE_EVENTS_FILE"
    check_file "$SOURCE_TEXT_FILE"

    log_step "Importing $SOURCE_EVENTS_FILE [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" -s "$SOURCE_EVENTS_FILE"

    log_step "Importing $SOURCE_TEXT_FILE [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" -s "$SOURCE_TEXT_FILE"
    ;;

  "smrpg")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_DIALOGUES_FILE="$DUMP_DIR/dialogues.txt"
    SOURCE_BATTLE_FILE="$DUMP_DIR/battleDialogues.txt"

    check_file "$SOURCE_DIALOGUES_FILE"
    check_file "$SOURCE_BATTLE_FILE"

    log_step "Importing $SOURCE_DIALOGUES_FILE [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" -s "$SOURCE_DIALOGUES_FILE" -g "$GAME_ID"

    log_step "Importing $SOURCE_BATTLE_FILE [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" -s "$SOURCE_BATTLE_FILE" -g "$GAME_ID"
    ;;

  "starocean")
    DUMP_DIR="$RESOURCE_PATH/chester/resources"
    SOURCE_FILE="$DUMP_DIR/dialogues.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" -s "$SOURCE_FILE" -g "$GAME_ID"
    ;;

  "rsaga")
    DUMP_DIR="$RESOURCE_PATH/dump_text"
    SOURCE_FILE_1="$DUMP_DIR/dump_english_dialogue.txt"

    check_file "$SOURCE_FILE_1"

    log_step "Importing $SOURCE_FILE_1 [game=${YELLOW}$GAME_ID${NC}]"
    python "$SCRIPT_DIR/manager.py" import_dump \
      -db "$DB" -s "$SOURCE_FILE_1"
    ;;

  *)
    log_error "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac

log_success "All tasks completed successfully!"
log_info "Database location: ${YELLOW}$DB${NC}"
