import os, csv

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

def read_dump(filename):
    buffer = {}
    with open(filename, 'r') as f:
        for line in f:
            if '[BLOCK ' in line:
                splitted_line = line.split(' ')
                block = int(splitted_line[1].replace(':', ''))
                offset_from = int(splitted_line[2], 16)
                offset_to = int(splitted_line[4].replace(']\n', ''), 16)
                buffer[block] = ['', [offset_from, offset_to]]
            else:
                buffer[block][0] += line
    return buffer

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
    translated_texts = []
    with open(filename, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            pointer_address = int(row.get('pointer_address', '0'), 16)
            text_address = int(row.get('text_address', '0'), 16)
            translated_texts.append((pointer_address, text_address, trans))
    return translated_texts
