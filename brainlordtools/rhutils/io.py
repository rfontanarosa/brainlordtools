__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

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

def write_byte(f, offset, byte):
    f.seek(offset)
    f.write(byte)

def fill(f, start_offset, length, byte=b'\x00') -> None:
    f.seek(start_offset)
    f.write(byte * length)