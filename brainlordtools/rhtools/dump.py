import os

def read_text(f, length=None, end_byte=None):
    text = b''
    if length:
        text = f.read(length)
    elif end_byte:
        byte = b'1'
        while not byte == end_byte:
            byte = f.read(1)
            if byte != end_byte:
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

def dump_gfx(f, start, end, path, filename):
    f.seek(start)
    block_size = end - start
    block = f.read(block_size)
    with open(os.path.join(path, filename), 'wb') as gfx_file:
        gfx_file.write(block)

def insert_gfx(f, start, end, path, filename):
    with open(os.path.join(path, filename), 'rb') as f1:
        block = f1.read()
        if len(block) == end - start:
            f.seek(start)
            f.write(block)
        else:
            raise Exception()
