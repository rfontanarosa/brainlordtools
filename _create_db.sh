#!/bin/bash

set -euo pipefail

GAME_ID=${1:-""}

if [ -z "$GAME_ID" ]; then
  echo "Usage: $0 <game_id>" >&2
  echo "  game_id  game to create the database for (e.g. som, brainlord, smrpg)" >&2
  exit 1
fi

source ./_common.sh

SCHEMA="$SCRIPT_DIR/schema/db.sql"

log_info "Starting database creation process"

check_file "$SCHEMA"

if [ -f "$DB" ]; then
    log_error "Database already exists: $DB"
    log_info "Delete it manually if you want to recreate it."
    exit 1
fi

mkdir -p "$(dirname "$DB")"

log_step "Applying schema to ${YELLOW}$DB${NC} [game=${YELLOW}$GAME_ID${NC}]"
sqlite3 "$DB" < "$SCHEMA"

log_success "All tasks completed successfully!"
log_info "Database location: ${YELLOW}$DB${NC}"
