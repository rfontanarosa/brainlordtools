#!/bin/bash

SOURCE_FILE_1=${1:-""}
SOURCE_FILE_2=${2:-""}
DESTINATION_FILE=${3:-""}

if [ -z "$SOURCE_FILE_1" ] || [ -z "$SOURCE_FILE_2" ] || [ -z "$DESTINATION_FILE" ]; then
    echo "Error: Missing arguments."
    echo "Usage: $0 <source_dump_1> <source_dump_2> <destination_diff_dump>"
    exit 1
fi

if [ ! -f "$SOURCE_FILE_1" ]; then
    echo "Error: Source file 1 not found: $SOURCE_FILE_1"
    exit 1
fi

if [ ! -f "$SOURCE_FILE_2" ]; then
    echo "Error: Source file 2 not found: $SOURCE_FILE_2"
    exit 1
fi

echo "Processing diff between $SOURCE_FILE_1 and $SOURCE_FILE_2..."

python -m brainlordutils.utils diff_dump \
    -s1 "$SOURCE_FILE_1" \
    -s2 "$SOURCE_FILE_2" \
    -d "$DESTINATION_FILE"

echo "Done! Diff saved to: $DESTINATION_FILE"
