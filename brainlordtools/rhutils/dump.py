import os, csv
from collections import OrderedDict

def read_text(f, offset, length=None, end_byte=None, cmd_list=None, append_end_byte=False):
    text = b''
    f.seek(offset)
    if length:
        text = f.read(length)
    elif end_byte:
        while True:
            byte = f.read(1)
            if cmd_list and byte in cmd_list.keys():
                text += byte
                bytes_to_read = cmd_list.get(byte)
                text += f.read(bytes_to_read)
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

def write_byte(f, offset, byte):
    f.seek(offset)
    f.write(byte)

def dump_binary(f, start, end, path, filename):
    f.seek(start)
    block = f.read(end - start)
    with open(os.path.join(path, filename), 'wb') as out:
        out.write(block)

def insert_binary(f, start, end, path, filename):
    with open(os.path.join(path, filename), 'rb') as f1:
        block = f1.read()
        if len(block) == end - start:
            f.seek(start)
            f.write(block)
        else:
            raise Exception()

def get_csv_translated_texts(filename):
    translated_texts = OrderedDict()
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            text_address = int(row['text_address'], 16)
            translated_texts[text_address] = trans
    return translated_texts
