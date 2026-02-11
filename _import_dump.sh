#!/bin/bash

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${YELLOW}--->${NC} $1"; }

check_file() {
    if [ ! -f "$1" ]; then
        log_error "Source file missing: $1"
        exit 1
    fi
}

GAME_ID=${1:-"som"}

BRAINLORD_PATH="$HOME/git"
RESOURCE_PATH="$BRAINLORD_PATH/brainlordresources/$GAME_ID"
DB="$RESOURCE_PATH/db/$GAME_ID.sqlite3"

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
