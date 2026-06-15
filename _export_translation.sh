#!/bin/bash

set -euo pipefail

GAME_ID=${1:-""}
USER=${2:-""}

if [ -z "$GAME_ID" ]; then
  echo "Usage: $0 <game_id> [user]" >&2
  echo "  game_id  game to export (e.g. som, brainlord, smrpg)" >&2
  echo "  user     optional translator; exports to a per-user file/dir" >&2
  exit 1
fi

source ./_common.sh

log_info "Starting export translation process for Game ID: ${YELLOW}$GAME_ID${NC}"

case "$GAME_ID" in
  "alcahest")
    if [ -n "$USER" ]; then
      TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translated_all_$USER/text"
      mkdir -p "$TRANSLATED_DUMP_DIR"

      log_step "Exporting $GAME_ID translation to $TRANSLATED_DUMP_DIR"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$TRANSLATED_DUMP_DIR" -u "$USER"
    else
      TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translated_all/text"
      mkdir -p "$TRANSLATED_DUMP_DIR"

      log_step "Exporting $GAME_ID translation to $TRANSLATED_DUMP_DIR"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$TRANSLATED_DUMP_DIR"
    fi
    ;;

  "7thsaga" | "brainlord" | "ignition" | "lufia" | "neugier" | "spike")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    mkdir -p "$TRANSLATED_DUMP_DIR"

    if [ -n "$USER" ]; then
      log_step "Exporting $GAME_ID translation to $DEST_USER_FILE"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_USER_FILE" -u "$USER"
    else
      log_step "Exporting $GAME_ID translation to $DEST_FILE"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_FILE"
    fi
    ;;

  "ffmq" | "soe")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dump_ita.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dump_ita_$USER.txt"

    mkdir -p "$TRANSLATED_DUMP_DIR"

    if [ -n "$USER" ]; then
      log_step "Exporting $GAME_ID translation to $DEST_USER_FILE"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_USER_FILE" -u "$USER" -g "$GAME_ID"
    else
      log_step "Exporting $GAME_ID translation to $DEST_FILE"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_FILE" -g "$GAME_ID"
    fi
    ;;

  "som" | "som_pal" | "smrpg")
    if [ -n "$USER" ]; then
      TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text_$USER"
      mkdir -p "$TRANSLATED_DUMP_DIR"

      log_step "Exporting $GAME_ID translation to $TRANSLATED_DUMP_DIR"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$TRANSLATED_DUMP_DIR" -u "$USER" -g "$GAME_ID"
    else
      TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text_ita"
      mkdir -p "$TRANSLATED_DUMP_DIR"

      log_step "Exporting $GAME_ID translation to $TRANSLATED_DUMP_DIR"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$TRANSLATED_DUMP_DIR" -g "$GAME_ID"
    fi
    ;;

  "starocean")
    TRANSLATED_DUMP_DIR="$RESOURCE_PATH/translation_text"
    DEST_FILE="$TRANSLATED_DUMP_DIR/dialogues.txt"
    DEST_USER_FILE="$TRANSLATED_DUMP_DIR/dialogues_$USER.txt"

    mkdir -p "$TRANSLATED_DUMP_DIR"

    if [ -n "$USER" ]; then
      log_step "Exporting $GAME_ID translation to $DEST_USER_FILE"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_USER_FILE" -u "$USER" -b 1 -g "$GAME_ID"
    else
      log_step "Exporting $GAME_ID translation to $DEST_FILE"
      python "$SCRIPT_DIR/manager.py" export_translation \
        -db "$DB" -d "$DEST_FILE" -b 1 -g "$GAME_ID"
    fi
    ;;

  *)
    log_error "Unknown GAME_ID: $GAME_ID"
    exit 1
    ;;
esac

log_success "All tasks completed successfully!"
log_info "Output location: ${YELLOW}$TRANSLATED_DUMP_DIR${NC}"
