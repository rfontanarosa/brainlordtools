__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

from typing import BinaryIO, Optional, Union

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

def write_text(
    f: BinaryIO,
    offset: int,
    text: bytes,
    length: Optional[int] = None,
    end_byte: Optional[bytes] = None,
    limit: Optional[int] = None
) -> int:
    """
    Writes a byte string to the specified offset with boundary checks.
    Returns: The file offset after the write operation finishes.
    """
    if length is not None and len(text) > length:
        raise ValueError(f"Text length ({len(text)}) exceeds fixed length ({length})")
    f.seek(offset)
    f.write(text)
    if end_byte is not None:
        f.write(end_byte)
    current_pos = f.tell()
    if limit is not None and current_pos > limit:
        raise BufferError(f"Write operation exceeded limit! Current: {hex(current_pos)}, Limit: {hex(limit)}")
    return current_pos

def write_byte(f: BinaryIO, offset: int, byte: Union[int, bytes])-> None:
    """
    Writes a single byte to the specified offset. 
    Converts integer values (0-255) to raw bytes automatically.
    """
    f.seek(offset)
    if isinstance(byte, int):
        byte = bytes([byte])
    f.write(byte)

def fill(f: BinaryIO, offset: int, length: int, byte: bytes = b'\x00') -> None:
    """
    Fills a region of the file with a specific byte pattern.
    Commonly used to clear SNES ROM free space.
    """
    f.seek(offset)
    f.write(byte * length)
