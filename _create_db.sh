#!/bin/bash

GAME_ID=${1:-"som"}

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
