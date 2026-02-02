__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, re

def read_text(f, offset=None, length=None, end_byte=None, cmd_list=None, append_end_byte=False):
    text = b''
    if offset is not None:
        f.seek(offset)
    if length:
        text = f.read(length)
    elif end_byte:
        while True:
            byte = f.read(1)
            if cmd_list and byte in cmd_list.keys():
                bytes_to_read = cmd_list.get(byte)
                text += byte + f.read(bytes_to_read)
            elif byte in end_byte:
                if append_end_byte:
                    text += byte
                break
            else:
                text += byte
    return text

def write_text(f, offset, text, length=None, end_byte=None, limit=None):
    if length and len(text) > length:
        raise Exception()
    f.seek(offset)
    f.write(text)
    if end_byte:
        f.write(end_byte)
    if limit and f.tell() > limit:
        raise Exception()
    return f.tell()

def read_dump(filename: str) -> dict:
    dump = {}
    current_id = None
    lines_accumulator = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if '[ID=' in line:
                if current_id is not None:
                    dump[current_id][0] = "".join(lines_accumulator)
                matches = re.findall(r'(\w+)=([^\s\]]+)', line)
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

def write_byte(f, offset, byte):
    f.seek(offset)
    f.write(byte)

def fill(f, start_offset, length, byte=b'\x00') -> None:
    f.seek(start_offset)
    f.write(byte * length)

def dump_binary(f, start_offset, length, filepath):
    f.seek(start_offset)
    block = f.read(length)
    with open(filepath, 'wb') as f1:
        f1.write(block)

def insert_binary(f, start_offset, filepath, max_length=None):
    with open(filepath, 'rb') as f1:
        block = f1.read()
        if max_length is not None and len(block) > max_length:
            raise ValueError(f"Insertion exceeds the specified limit of {max_length} bytes.")
        f.seek(start_offset)
        f.write(block)

def get_csv_translated_texts(filename):
    translated_texts = []
    with open(filename, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            pointer_address = int(row.get('pointer_address', '0'), 16)
            text_address = int(row.get('text_address', '0'), 16)
            translated_texts.append((pointer_address, text_address, trans))
    return translated_texts
