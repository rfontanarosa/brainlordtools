#!/bin/bash

set -euo pipefail

GAME_ID=${1:-""}
USER=${2:-""}

if [ -z "$GAME_ID" ] || [ -z "$USER" ]; then
  echo "Usage: $0 <game_id> <user>" >&2
  echo "  game_id  game to import (e.g. som, brainlord, smrpg)" >&2
  echo "  user     translator whose file/dir to import (required)" >&2
  exit 1
fi

source ./_common.sh

log_info "Starting import translation process"

case "$GAME_ID" in
  "brainlord")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/dump_text"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dump_eng.txt"

    check_file "$SOURCE_FILE"
    check_file "$ORIGINAL_DUMP_PATH"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
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

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
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

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
    python "$SCRIPT_DIR/manager.py" import_translation \
      -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH"
    ;;

  "7thsaga" | "ignition" | "spike")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
    python "$SCRIPT_DIR/manager.py" import_translation \
      -db "$DB" -s "$SOURCE_FILE" -u "$USER"
    ;;

  "rsaga")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translated_text"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dump_italian_${USER}_dialogue.txt"

    check_file "$SOURCE_FILE"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
    python "$SCRIPT_DIR/manager.py" import_translation \
      -db "$DB" -s "$SOURCE_FILE" -u "$USER"
    ;;

  "som" | "som_pal")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_EVENTS_FILE="$TRANSLATED_DUMP_DIR/dump_events_$USER.txt"
    SOURCE_TEXT_FILE="$TRANSLATED_DUMP_DIR/dump_texts_$USER.txt"

    check_file "$SOURCE_EVENTS_FILE"
    check_file "$SOURCE_TEXT_FILE"

    log_step "Importing $SOURCE_EVENTS_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
    python "$SCRIPT_DIR/manager.py" import_translation \
      -db "$DB" -s "$SOURCE_EVENTS_FILE" -u "$USER"

    log_step "Importing $SOURCE_TEXT_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
    python "$SCRIPT_DIR/manager.py" import_translation \
      -db "$DB" -s "$SOURCE_TEXT_FILE" -u "$USER"
    ;;

  "smrpg")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    SOURCE_DIALOGUES_FILE="$TRANSLATED_DUMP_DIR/dialogues_ita_$USER.txt"
    SOURCE_BATTLE_FILE="$TRANSLATED_DUMP_DIR/battleDialogues_ita_$USER.txt"

    check_file "$SOURCE_DIALOGUES_FILE"
    check_file "$SOURCE_BATTLE_FILE"

    log_step "Importing $SOURCE_DIALOGUES_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
    python "$SCRIPT_DIR/manager.py" import_translation \
      -db "$DB" -s "$SOURCE_DIALOGUES_FILE" -u "$USER" -g "$GAME_ID"

    log_step "Importing $SOURCE_BATTLE_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
    python "$SCRIPT_DIR/manager.py" import_translation \
      -db "$DB" -s "$SOURCE_BATTLE_FILE" -u "$USER" -g "$GAME_ID"
    ;;

  "starocean")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/chester/translated"
    SOURCE_FILE="$TRANSLATED_DUMP_DIR/dialogues.txt"
    ORIGINAL_DUMP_DIR="$RESOURCE_PATH/chester/resources"
    ORIGINAL_DUMP_PATH="$ORIGINAL_DUMP_DIR/dialogues.txt"

    check_file "$SOURCE_FILE"
    check_file "$ORIGINAL_DUMP_PATH"

    log_step "Importing $SOURCE_FILE [game=${YELLOW}$GAME_ID${NC}, user=${YELLOW}$USER]${NC}"
    python "$SCRIPT_DIR/manager.py" import_translation \
      -db "$DB" -s "$SOURCE_FILE" -u "$USER" -od "$ORIGINAL_DUMP_PATH" -g "$GAME_ID"
    ;;

  *)
    log_error "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac

log_success "All tasks completed successfully!"
log_info "Database location: ${YELLOW}$DB${NC}"
