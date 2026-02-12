#!/bin/bash

SOURCE_FILE_1=${1:-""}
SOURCE_FILE_2=${2:-""}
DESTINATION_FILE=${3:-""}

source ./_common.sh

if [ -z "$SOURCE_FILE_1" ] || [ -z "$SOURCE_FILE_2" ] || [ -z "$DESTINATION_FILE" ]; then
    log_error "Missing arguments."
    echo "Usage: $0 <source_dump_1> <source_dump_2> <destination_diff_dump>"
    exit 1
fi

check_file "$SOURCE_FILE_1"
check_file "$SOURCE_FILE_2"

log_info "Processing diff between $SOURCE_FILE_1 and $SOURCE_FILE_2..."

python "$SCRIPT_DIR/manager.py" diff_dump \
    -s1 "$SOURCE_FILE_1" \
    -s2 "$SOURCE_FILE_2" \
    -d "$DESTINATION_FILE"

log_success "Done! Diff saved to: $DESTINATION_FILE"
