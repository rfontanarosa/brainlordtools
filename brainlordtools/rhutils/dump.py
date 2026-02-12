__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, re

HEADER_PATTERN = r'(\w+)=([^\s\]]+)'

def read_dump(filename: str) -> dict:
    dump = {}
    current_id = None
    lines_accumulator = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('[ID='):
                if current_id is not None:
                    dump[current_id][0] = "".join(lines_accumulator)
                matches = re.findall(HEADER_PATTERN, line)
                metadata = dict(matches)
                current_id = int(metadata['ID'])
                text_offset_from = int(metadata['START'], 16)
                text_offset_to = int(metadata['END'], 16)
                pointers_str = metadata.get('POINTERS', '')
                pointer_offsets = [int(p, 16) for p in pointers_str.split(';') if p.strip()]
                dump[current_id] = ['', [text_offset_from, text_offset_to], pointer_offsets]
                lines_accumulator = []
            else:
                if current_id is not None:
                    lines_accumulator.append(line)
        if current_id is not None:
            dump[current_id][0] = "".join(lines_accumulator)
    return dump

def extract_binary(f, start_offset, length, file_path) -> None:
    """Extracts a specific block of bytes from the opened file to a new file."""
    f.seek(start_offset)
    block = f.read(length)
    if len(block) < length:
        print(f"Warning: Requested {length} bytes, but only read {len(block)} before EOF.")
    with open(file_path, 'wb') as f_out:
        f_out.write(block)

def insert_binary(f, start_offset, file_path, max_length=None) -> None:
    """Inserts a binary file into the opened file at a specific offset."""
    with open(file_path, 'rb') as f_in:
        block = f_in.read()
        if max_length is not None and len(block) > max_length:
            raise ValueError(f"Error: {file_path} ({len(block)} bytes) exceeds the limit of {max_length} bytes!")
        f.seek(start_offset)
        f.write(block)

def get_csv_translated_texts(filename):
    """Parses a CSV file into a list of (pointer_address, text_address, translation) tuples with hex-to-int conversion."""
    translated_texts = []
    with open(filename, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            pointer_address = int(row.get('pointer_address', '0'), 16)
            text_address = int(row.get('text_address', '0'), 16)
            translated_texts.append((pointer_address, text_address, trans))
    return translated_texts
